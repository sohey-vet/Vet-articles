#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_refs.py — 参照文献のPubMed照合ゲート

2026-09-08 の参照文献監査（全111記事・577文献 / 要対応193件）を受けて新設。
最重症は「誌名・巻・号・頁は実在論文と一致するのにタイトルだけ別物」＝
実在論文の書誌に架空タイトルを被せた**合成捏造**。これを機械的に検出する。

使い方:
    python scripts/verify_refs.py topics/救急/DIC_診断と治療.html
    python scripts/verify_refs.py --all --out refs_report.csv
    python scripts/verify_refs.py --all --dry-run          # PubMedを叩かず抽出だけ
    python scripts/verify_refs.py <記事> --pmid-cache .refcache.json

判定:
    OK        実在が確認でき、タイトル・誌名・年・巻号頁が一致
    書誌誤り   論文は実在するが、記事側の誌名/年/巻号頁/著者のいずれかが誤り
    合成疑い   記事のタイトルに一致する論文が無い（特に巻号頁が実在論文と一致する場合は最重症）
    不在      どの検索でも候補ゼロ。文献として成立していない
    対象外    ガイドライン・ポジションステートメント・書籍等（PubMed対象外・手動確認要）
    要再照合   PubMedに到達できず未検証（通信障害を「合成疑い」に化けさせないための区分）

終了コード:
    0 = 合成疑い・不在・要再照合ともに0件（ゲート通過）
    1 = 合成疑い / 不在 / 要再照合 が1件以上
    2 = 実行エラー（抽出失敗など）

制約（監査時に判明した限界。ここを疑ってから人間が再確認する）:
    - JAAHA/JSAP 等の略誌名は [Journal] 検索で引けない → JOURNAL_ALIASES で正式TAへ展開する
    - 団体著者（ACVIM/AAHA等）は著者検索から漏れる
    - PubMed非収載誌（Today's Veterinary Practice / dvm360 等）は「対象外」に落ちる
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

# Windows cp932 コンソールで丸数字・絵文字がクラッシュするため必ず utf-8 化する
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("bs4 が必要です: pip install beautifulsoup4", file=sys.stderr)
    raise

SCRIPT_DIR = Path(__file__).resolve().parent
SITE_ROOT = SCRIPT_DIR.parent
TOPICS_DIR = SITE_ROOT / "topics"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
USER_AGENT = "VetEvidence-verify-refs/1.0 (+https://pawmedicaljp.com)"

V_OK = "OK"
V_BIB = "書誌誤り"
V_SYNTH = "合成疑い"
V_MISSING = "不在"
V_OUT = "対象外"
V_RETRY = "要再照合"   # E-utilities 障害で照合できなかった＝未検証。通信失敗を「合成疑い」に化けさせない
FAIL_VERDICTS = (V_SYNTH, V_MISSING, V_RETRY)


class EutilsError(RuntimeError):
    pass

# ---------------------------------------------------------------- 誌名の正規化

JOURNAL_ALIASES = {
    "javma": "J Am Vet Med Assoc",
    "jvim": "J Vet Intern Med",
    "jvecc": "J Vet Emerg Crit Care",
    "jaaha": "J Am Anim Hosp Assoc",
    "jsap": "J Small Anim Pract",
    "jfms": "J Feline Med Surg",
    "jvms": "J Vet Med Sci",
    "vet emerg crit care": "J Vet Emerg Crit Care",
    "j vet emerg crit care san antonio": "J Vet Emerg Crit Care",
    "vet clin north am small anim pract": "Vet Clin North Am Small Anim Pract",
    "compend contin educ vet": "Compend Contin Educ Vet",
    "am j vet res": "Am J Vet Res",
    "n engl j med": "N Engl J Med",
}

# PubMed に載らない媒体（誌名が一致したら即「対象外」）
NON_PUBMED_JOURNALS = (
    "today's veterinary practice",
    "todays veterinary practice",
    "dvm360",
    "veterinary practice news",
    "clinician's brief",
    "clinicians brief",
    "vin",
)

# 書籍・ガイドライン・教科書の指標
OUT_OF_SCOPE_PATTERNS = (
    r"\b\d+(?:st|nd|rd|th)\s+ed(?:ition)?\b",
    r"\(\s*\d+(?:st|nd|rd|th)\s+ed\.?\s*\)",
    r"\bed\.\s*(?:19|20)\d{2}",
    r"\bIn:\s",
    r"\bHandbook\b",
    r"\bManual\b",
    r"\bTextbook\b",
    r"\bPlumb'?s\b",
    r"\bBSAVA\b",
    r"\bElsevier\b",
    r"\bWiley\b",
    r"\bBlackwell\b",
    r"\bSaunders;\b",
    r"\bMosby\b",
    r"\bTeton\b",
    r"\bWSAVA\b\s+.*\bGuidelines?\b",
    r"\bAAHA\b\s+.*\bGuidelines?\b",
    r"\bAAFP\b\s+.*\bGuidelines?\b",
    r"\bPosition\s+Statement\b",
    r"\bWhite\s+Paper\b",
    r"\bAccessed\b",
    r"https?://",
)

STOPWORDS = {
    "a", "an", "and", "the", "of", "in", "on", "for", "with", "to", "from",
    "by", "as", "at", "or", "its", "their", "study", "cases", "case", "review",
    "using", "after", "during", "into", "between", "versus", "vs",
}


def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s)


def squash(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def norm_title(s: str) -> str:
    s = nfkc(s or "").lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def sim(a: str, b: str) -> float:
    a, b = norm_title(a), norm_title(b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def norm_journal(s: str) -> str:
    s = nfkc(s or "").lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return JOURNAL_ALIASES.get(s, s).lower() if s in JOURNAL_ALIASES else s


def expand_journal(s: str) -> str:
    """記事側の略誌名を PubMed の TA（正式略誌名）へ展開する。"""
    key = norm_journal(s)
    return JOURNAL_ALIASES.get(key, squash(s))


def journal_equal(a: str, b: str) -> bool:
    na, nb = norm_journal(expand_journal(a)), norm_journal(expand_journal(b))
    if not na or not nb:
        return False
    if na == nb:
        return True
    return na.startswith(nb) or nb.startswith(na)


def first_page(pages: str) -> str:
    if not pages:
        return ""
    m = re.match(r"\s*([A-Za-z]?\d+)", nfkc(pages))
    return m.group(1) if m else ""


def pages_equal(a: str, b: str) -> bool:
    fa, fb = first_page(a), first_page(b)
    return bool(fa) and fa == fb


# ---------------------------------------------------------------- 文献の抽出

class Ref:
    __slots__ = ("num", "raw", "authors", "title", "journal", "year",
                 "volume", "issue", "pages", "first_author", "em_journals")

    def __init__(self, num, raw):
        self.num = num
        self.raw = raw
        self.authors = ""
        self.title = ""
        self.journal = ""
        self.year = ""
        self.volume = ""
        self.issue = ""
        self.pages = ""
        self.first_author = ""
        self.em_journals = []

    def key(self) -> str:
        return hashlib.sha1(norm_title(self.raw).encode("utf-8")).hexdigest()

    def bib_str(self) -> str:
        v = self.volume + (f"({self.issue})" if self.issue else "")
        tail = ";".join(x for x in [self.year, v] if x)
        if self.pages:
            tail += f":{self.pages}"
        return squash(f"{self.journal} {tail}")


def extract_from_html(path: Path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    div = soup.find("div", id="refs")
    if div is None:
        return []
    ol = div.find("ol")
    if ol is None:
        return []
    refs = []
    for i, li in enumerate(ol.find_all("li"), start=1):
        r = Ref(i, squash(li.get_text(" ", strip=True)))
        r.em_journals = [squash(em.get_text(" ", strip=True)) for em in li.find_all("em")]
        refs.append(r)
    return refs


MD_REF_HEAD = re.compile(r"^##\s*.*参[照考]\s*論文")
MD_REF_ITEM = re.compile(r"^\s*(\d+)\.\s+(.*)$")


def extract_from_md(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    refs, in_refs, cur = [], False, None
    for line in lines:
        if line.startswith("## "):
            if MD_REF_HEAD.match(line):
                in_refs = True
                continue
            if in_refs:
                break
            continue
        if not in_refs:
            continue
        if line.strip().startswith("---"):
            break
        m = MD_REF_ITEM.match(line)
        if m:
            cur = Ref(int(m.group(1)), squash(m.group(2)))
            refs.append(cur)
        elif cur is not None and line.strip():
            cur.raw = squash(cur.raw + " " + line.strip())
    return refs


def extract(path: Path):
    if path.suffix.lower() in (".html", ".htm"):
        return extract_from_html(path)
    return extract_from_md(path)


# ---------------------------------------------------------------- 書誌のパース

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
# 「Stafford Johnson M, Martin M, ...」のような複合姓も拾う
AUTHOR_HEAD_RE = re.compile(r"^(?:[A-Z][A-Za-z'’\-]+\s+)+[A-Z]{1,3}\b(?=\s*[,;]|\s*$)")
FIRST_AUTHOR_RE = re.compile(
    r"^((?:[A-Z][A-Za-z'’\-]+\s+)*?[A-Z][A-Za-z'’\-]+)\s+([A-Z]{1,3})\b(?=\s*[,;]|\s*$|\s+et\b)")
JOURNALish_RE = re.compile(
    r"^(?:J\b|JAVMA|JVIM|JVECC|JAAHA|JSAP|JFMS|JVMS|Vet\b|Am J\b|Aust\b|Can\b|Ir\b|"
    r"BMC\b|Front\b|PLoS\b|N Engl\b|Top\b|Clin\b|Compend\b|Anim\b|Res Vet\b|Small Anim\b|"
    r"Acta\b|Sci Rep\b|Animals\b|Pathogens\b|Microorganisms\b|Viruses\b|Vaccines\b)",
    re.IGNORECASE,
)


def pick_year(text: str):
    """『年;巻』の年を優先して選ぶ（本文中の (1987-1993) 等に釣られないため）。"""
    cands = list(YEAR_RE.finditer(text))
    if not cands:
        return None
    for m in cands:
        rest = text[m.end():m.end() + 3]
        if rest.lstrip().startswith(";"):
            return m
    return cands[-1]


def looks_like_journal(seg: str) -> bool:
    seg = squash(seg).strip(" ,.;:")
    if not seg or len(seg.split()) > 9:
        return False
    if JOURNALish_RE.match(seg):
        return True
    if norm_journal(seg) in JOURNAL_ALIASES:
        return True
    words = [w for w in seg.split() if w]
    caps = sum(1 for w in words if w[:1].isupper())
    return len(words) <= 6 and caps >= max(1, len(words) - 1)


def parse_ref(r: Ref) -> Ref:
    t = squash(nfkc(r.raw))
    ym = pick_year(t)

    if ym:
        r.year = ym.group(0)
        head = t[:ym.start()].strip(" ,.;:")
        tail = t[ym.end():]
        m = re.match(r"\s*;\s*(\d+)\s*(?:\(\s*([^)]*?)\s*\))?\s*(?::\s*([^\s;.]+))?", tail)
        if m:
            r.volume = m.group(1) or ""
            r.issue = (m.group(2) or "").strip()
            r.pages = (m.group(3) or "").strip().rstrip(".")
        else:
            m2 = re.search(r"\b(\d+)\s*\(\s*([^)]*?)\s*\)\s*:\s*([^\s;.]+)", tail)
            if m2:
                r.volume, r.issue, r.pages = m2.group(1), m2.group(2), m2.group(3).rstrip(".")
    else:
        head = t.strip(" ,.;:")

    # 誌名は <em> があればそれを優先（年の直前に来る <em> を採る）
    em_j = ""
    for em in r.em_journals:
        if em and looks_like_journal(em):
            em_j = em
    segs = [s.strip(" ,.;:") for s in re.split(r"\.\s+", head) if s.strip(" ,.;:")]

    if em_j:
        r.journal = em_j
        idx = head.rfind(em_j)
        before = head[:idx].strip(" ,.;:") if idx > 0 else head
        segs = [s.strip(" ,.;:") for s in re.split(r"\.\s+", before) if s.strip(" ,.;:")]
    elif segs and looks_like_journal(segs[-1]):
        r.journal = segs[-1]
        segs = segs[:-1]

    if segs:
        if AUTHOR_HEAD_RE.match(segs[0]) or "et al" in segs[0].lower():
            r.authors = segs[0]
            r.title = ". ".join(segs[1:])
        else:
            r.title = ". ".join(segs)
    if not r.title and r.authors:
        r.title, r.authors = r.authors, ""

    r.title = r.title.strip(" ,.;:")
    am = FIRST_AUTHOR_RE.match(r.authors)
    if am:
        r.first_author = f"{am.group(1)} {am.group(2)}"
    return r


def is_out_of_scope(r: Ref) -> str:
    """PubMed対象外なら理由を返す。対象なら空文字。"""
    for pat in OUT_OF_SCOPE_PATTERNS:
        m = re.search(pat, r.raw, re.IGNORECASE)
        if m:
            return f"書籍/ガイドライン指標: 「{squash(m.group(0))}」"
    jn = norm_journal(r.journal)
    for bad in NON_PUBMED_JOURNALS:
        if jn and (jn == norm_journal(bad) or norm_journal(bad) in jn):
            return f"PubMed非収載誌: {r.journal}"
    return ""


# ---------------------------------------------------------------- PubMed 照合

class Pubmed:
    def __init__(self, sleep=0.4, api_key=None, timeout=30):
        self.sleep = sleep
        self.api_key = api_key
        self.timeout = timeout
        self._last = 0.0
        self.calls = 0

    def _get(self, endpoint, params):
        p = dict(params)
        p.setdefault("tool", "vetevidence-verify-refs")
        p.setdefault("email", "info@pawmedicaljp.com")
        if self.api_key:
            p["api_key"] = self.api_key
        url = EUTILS + endpoint + "?" + urllib.parse.urlencode(p)
        wait = self.sleep - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        last_err = None
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8", "replace")
                self._last = time.time()
                self.calls += 1
                return body
            except Exception as e:  # noqa: BLE001
                last_err = e
                time.sleep(2.0 * (attempt + 1))
        self._last = time.time()
        raise EutilsError(f"E-utilities 失敗: {last_err}")

    def esearch(self, term, retmax=10):
        body = self._get("esearch.fcgi", {
            "db": "pubmed", "term": term, "retmode": "json", "retmax": retmax,
        })
        try:
            data = json.loads(body)
        except Exception as e:  # noqa: BLE001
            raise EutilsError(f"esearch のJSONを解釈できません: {e}") from e
        return data.get("esearchresult", {}).get("idlist", []) or []

    def esummary(self, pmids):
        if not pmids:
            return []
        body = self._get("esummary.fcgi", {
            "db": "pubmed", "id": ",".join(pmids), "retmode": "json",
        })
        try:
            data = json.loads(body).get("result", {})
        except Exception as e:  # noqa: BLE001
            raise EutilsError(f"esummary のJSONを解釈できません: {e}") from e
        out = []
        for pid in data.get("uids", []):
            d = data.get(pid, {})
            authors = [a.get("name", "") for a in d.get("authors", []) if a.get("authtype") == "Author"]
            ym = re.search(r"(?:19|20)\d{2}", f"{d.get('pubdate','')} {d.get('sortpubdate','')}")
            out.append({
                "pmid": pid,
                "title": squash(re.sub(r"<[^>]+>", "", d.get("title", ""))).rstrip("."),
                "journal": squash(d.get("source", "")),
                "fulljournal": squash(d.get("fulljournalname", "")),
                "volume": squash(d.get("volume", "")),
                "issue": squash(d.get("issue", "")),
                "pages": squash(d.get("pages", "")) or squash(d.get("elocationid", "")),
                "year": ym.group(0) if ym else "",
                "authors": authors,
                "first_author": authors[0] if authors else "",
            })
        return out

    def efetch_abstract(self, pmid):
        try:
            return self._get("efetch.fcgi", {
                "db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text",
            })
        except Exception:
            return ""


def q(s: str) -> str:
    """PubMed のクエリ用にクォート内で問題になる文字を落とす。"""
    s = nfkc(s or "")
    s = re.sub(r'["\[\]()]', " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def title_keywords(title, n=4):
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", nfkc(title or ""))
             if w.lower() not in STOPWORDS]
    seen, out = set(), []
    for w in words:
        lw = w.lower()
        if lw not in seen:
            seen.add(lw)
            out.append(w)
        if len(out) >= n:
            break
    return out


def compare_bib(r: Ref, s: dict):
    """記事側 vs PubMed の書誌差分リストを返す。"""
    diffs = []
    if r.journal and s.get("journal") and not journal_equal(r.journal, s["journal"]) \
            and not journal_equal(r.journal, s.get("fulljournal", "")):
        diffs.append(f"誌名: 記事『{r.journal}』 / 実際『{s['journal']}』")
    if r.year and s.get("year") and r.year != s["year"]:
        diffs.append(f"年: 記事{r.year} / 実際{s['year']}")
    if r.volume and s.get("volume") and r.volume != s["volume"]:
        diffs.append(f"巻: 記事{r.volume} / 実際{s['volume']}")
    if r.pages and s.get("pages") and not pages_equal(r.pages, s["pages"]):
        diffs.append(f"頁: 記事{r.pages} / 実際{s['pages']}")
    if r.first_author and s.get("first_author"):
        # PubMed は "Scott Weese J" のように姓の分割が記事側と異なることがあるため、
        # 姓トークンが全著者名のどこかに現れるかで判定する（誤検出を避ける）
        surname = norm_title(r.first_author).split()[0]
        pool = " ".join(norm_title(a) for a in (s.get("authors") or [s["first_author"]]))
        if len(surname) >= 3 and surname not in pool.split():
            diffs.append(f"第一著者: 記事『{r.first_author}』 / 実際『{s['first_author']}』")
    return diffs


def fmt_hit(s: dict) -> str:
    v = s.get("volume", "")
    if s.get("issue"):
        v += f"({s['issue']})"
    return (f"PMID {s['pmid']} | {s['title']} | "
            f"{s.get('journal','')} {s.get('year','')};{v}:{s.get('pages','')}")


def verify_ref(r: Ref, pm: Pubmed):
    """1件を照合して {verdict, evidence, pmid, note} を返す。"""
    reason = is_out_of_scope(r)
    if reason:
        return {"verdict": V_OUT, "pmid": "", "evidence": "",
                "note": f"{reason} / 発行元サイトで手動確認要"}

    has_slot = bool(r.journal and r.year and r.volume and first_page(r.pages))
    if not r.title or (len(norm_title(r.title)) < 12 and not has_slot):
        # 著者・誌名・巻号頁が無く、特定文献を指していない説明文の類
        kws = title_keywords(r.raw, 4)
        ids = pm.esearch(" AND ".join(f"{k}[Title]" for k in kws)) if len(kws) >= 2 else []
        if not ids:
            return {"verdict": V_MISSING, "pmid": "", "evidence": "",
                    "note": "タイトル・著者・書誌が抽出できず、検索でも候補ゼロ。文献として成立していない"}
        cands = pm.esummary(ids[:5])
        best = max(cands, key=lambda s: sim(r.raw, s["title"])) if cands else None
        return {"verdict": V_SYNTH, "pmid": best["pmid"] if best else "",
                "evidence": fmt_hit(best) if best else "",
                "note": "書誌が不完全（要約表現/説明文の可能性）。近似候補のみ"}

    candidates = []
    slot_conflict = None  # 巻号頁のスロットを占有する「別タイトルの実在論文」

    # ① 書誌スロット照合 ── 巻号頁が一致するのにタイトルが別物＝合成捏造の最重症
    fp = first_page(r.pages)
    if has_slot:
        ta = expand_journal(r.journal)
        term = f'"{q(ta)}"[Journal] AND {r.year}[DP] AND {r.volume}[VI] AND {fp}[PG]'
        slot_ids = pm.esearch(term, retmax=5)
        if not slot_ids:
            # 略誌名が [Journal] で引けない場合の保険（誌名条件を外して巻・頁で絞る）
            slot_ids = pm.esearch(f"{r.year}[DP] AND {r.volume}[VI] AND {fp}[PG]", retmax=20)
        if slot_ids:
            occupants = [s for s in pm.esummary(slot_ids)
                         if journal_equal(r.journal, s.get("journal", ""))
                         or journal_equal(r.journal, s.get("fulljournal", ""))]
            if occupants:
                candidates.extend(occupants)
                best = max(occupants, key=lambda s: sim(r.title, s["title"]))
                score = sim(r.title, best["title"])
                if score >= 0.85:
                    diffs = compare_bib(r, best)
                    if not diffs:
                        return {"verdict": V_OK, "pmid": best["pmid"],
                                "evidence": fmt_hit(best), "note": "書誌スロット一致"}
                    return {"verdict": V_BIB, "pmid": best["pmid"],
                            "evidence": fmt_hit(best), "note": " / ".join(diffs)}
                slot_conflict = (best, score)

    # ② タイトル完全一致検索
    ids = pm.esearch(f'"{q(r.title)}"[Title]', retmax=5)
    if ids:
        hits = pm.esummary(ids)
        candidates.extend(hits)
        best = max(hits, key=lambda s: sim(r.title, s["title"])) if hits else None
        if best and sim(r.title, best["title"]) >= 0.90:
            diffs = compare_bib(r, best)
            if not diffs:
                return {"verdict": V_OK, "pmid": best["pmid"],
                        "evidence": fmt_hit(best), "note": "タイトル一致・書誌一致"}
            if slot_conflict:
                diffs.append(f"※ 記事の巻号頁には別論文（PMID {slot_conflict[0]['pmid']}）が載っている")
            return {"verdict": V_BIB, "pmid": best["pmid"], "evidence": fmt_hit(best),
                    "note": " / ".join(diffs)}

    # タイトルが実在せず、かつ巻号頁に別論文が載っている＝合成捏造の最重症
    if slot_conflict:
        best, score = slot_conflict
        return {"verdict": V_SYNTH, "pmid": best["pmid"], "evidence": fmt_hit(best),
                "note": ("★最重症: 記事の誌名・巻・頁は実在論文と一致するが"
                         f"タイトルが別物（タイトル一致度 {score:.2f}）。"
                         "実在論文の書誌に架空タイトルが乗っている疑い")}

    # ③ 第一著者 + 年 + タイトル主要語
    kws = title_keywords(r.title, 3)
    if r.first_author and len(kws) >= 2:
        au = r.first_author.replace(".", "")
        term = f'"{q(au)}"[Author]'
        if r.year:
            term += f" AND {r.year}[DP]"
        term += " AND (" + " OR ".join(f"{k}[Title]" for k in kws) + ")"
        ids3 = pm.esearch(term, retmax=10)
        if not ids3 and r.year:
            ids3 = pm.esearch(f'"{q(au)}"[Author] AND (' +
                              " AND ".join(f"{k}[Title]" for k in kws[:2]) + ")", retmax=10)
        if ids3:
            hits = pm.esummary(ids3)
            candidates.extend(hits)
            best = max(hits, key=lambda s: sim(r.title, s["title"]))
            if sim(r.title, best["title"]) >= 0.88:
                diffs = compare_bib(r, best) or ["（書誌差分なし・①で拾えなかっただけの可能性）"]
                return {"verdict": V_BIB, "pmid": best["pmid"], "evidence": fmt_hit(best),
                        "note": " / ".join(diffs)}

    # ④ タイトル主要語のみで広域検索
    kws4 = title_keywords(r.title, 4)
    if len(kws4) >= 2:
        ids4 = pm.esearch(" AND ".join(f"{k}[Title]" for k in kws4), retmax=10)
        if not ids4:
            ids4 = pm.esearch(" AND ".join(f"{k}[Title]" for k in kws4[:2]), retmax=10)
        if ids4:
            candidates.extend(pm.esummary(ids4[:5]))

    if candidates:
        best = max(candidates, key=lambda s: sim(r.title, s["title"]))
        score = sim(r.title, best["title"])
        if score >= 0.90:
            diffs = compare_bib(r, best)
            if not diffs:
                return {"verdict": V_OK, "pmid": best["pmid"],
                        "evidence": fmt_hit(best), "note": "広域検索で一致"}
            return {"verdict": V_BIB, "pmid": best["pmid"], "evidence": fmt_hit(best),
                    "note": " / ".join(diffs)}
        return {"verdict": V_SYNTH, "pmid": best["pmid"], "evidence": fmt_hit(best),
                "note": f"記事タイトルに一致する論文なし（最大一致 {score:.2f}）。"
                        "複数の実在論文の要素が混ざった合成の疑い"}

    return {"verdict": V_MISSING, "pmid": "", "evidence": "",
            "note": "タイトル検索・著者検索・広域検索のいずれも候補ゼロ"}


# ---------------------------------------------------------------- 実行

def collect_targets(paths, use_all):
    if use_all:
        htmls = sorted(TOPICS_DIR.rglob("*.html"))
        stems = {(p.parent, p.stem) for p in htmls}
        mds = [p for p in sorted(TOPICS_DIR.rglob("*.md")) if (p.parent, p.stem) not in stems]
        return htmls + mds
    out = []
    for p in paths:
        pp = Path(p)
        if not pp.is_absolute():
            cand = SITE_ROOT / p
            pp = cand if cand.exists() else pp
        if pp.is_dir():
            out.extend(sorted(pp.rglob("*.html")))
        else:
            out.append(pp)
    return out


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(SITE_ROOT))
    except Exception:
        return str(p)


def main():
    ap = argparse.ArgumentParser(description="参照文献のPubMed照合ゲート")
    ap.add_argument("paths", nargs="*", help="記事HTML または md のパス（複数可）")
    ap.add_argument("--all", action="store_true", help="topics配下の全記事を対象にする")
    ap.add_argument("--dry-run", action="store_true", help="PubMedを叩かず抽出結果だけ表示")
    ap.add_argument("--out", help="判定結果を書き出すCSVパス")
    ap.add_argument("--pmid-cache", help="照合結果キャッシュJSON（同じ文献を再照合しない）")
    ap.add_argument("--api-key", default=os.environ.get("NCBI_API_KEY"), help="NCBI APIキー（任意）")
    ap.add_argument("--sleep", type=float, default=0.4, help="リクエスト間隔秒（既定0.4=2.5req/s）")
    ap.add_argument("--quiet-ok", action="store_true", help="OK/対象外の明細を出さない")
    args = ap.parse_args()

    targets = collect_targets(args.paths, args.all)
    if not targets:
        print("対象がありません。記事パスを指定するか --all を付けてください。", file=sys.stderr)
        return 2

    cache = {}
    cache_path = Path(args.pmid_cache) if args.pmid_cache else None
    if cache_path and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    pm = None if args.dry_run else Pubmed(sleep=args.sleep, api_key=args.api_key)
    rows = []
    totals = {V_OK: 0, V_BIB: 0, V_SYNTH: 0, V_MISSING: 0, V_OUT: 0, V_RETRY: 0}
    n_extracted = 0
    missing_refs_files = []

    try:
        for path in targets:
            if not path.exists():
                print(f"[skip] ファイルが見つかりません: {path}", file=sys.stderr)
                continue
            refs = [parse_ref(r) for r in extract(path)]
            n_extracted += len(refs)
            print(f"\n=== {rel(path)} ── 参照論文 {len(refs)}件 ===")
            if not refs:
                missing_refs_files.append(rel(path))
                print("  ⚠ 参照論文セクションが空、または抽出できませんでした")
                continue

            for r in refs:
                if args.dry_run:
                    print(f"  [{r.num}] 著者: {r.authors or '-'}")
                    print(f"       タイトル: {r.title or '-'}")
                    print(f"       書誌: {r.bib_str() or '-'}")
                    oos = is_out_of_scope(r)
                    if oos:
                        print(f"       → 対象外候補: {oos}")
                    rows.append({
                        "file": rel(path), "ref_no": r.num, "verdict": "(dry-run)",
                        "authors": r.authors, "title": r.title, "bib": r.bib_str(),
                        "pmid": "", "evidence": "", "note": is_out_of_scope(r),
                        "raw": r.raw,
                    })
                    continue

                key = r.key()
                res = cache.get(key)
                cached = res is not None
                if not cached:
                    try:
                        res = verify_ref(r, pm)
                    except EutilsError as e:
                        time.sleep(5)
                        try:  # 通信障害は1回だけ丸ごとリトライする
                            res = verify_ref(r, pm)
                        except EutilsError:
                            res = {"verdict": V_RETRY, "pmid": "", "evidence": "",
                                   "note": f"PubMedに到達できず未検証: {e}"}
                    if res["verdict"] != V_RETRY:
                        cache[key] = res
                totals[res["verdict"]] = totals.get(res["verdict"], 0) + 1

                mark = {V_OK: "○", V_BIB: "△", V_SYNTH: "✖",
                        V_MISSING: "✖", V_OUT: "―", V_RETRY: "?"}[res["verdict"]]
                if res["verdict"] in (V_OK, V_OUT) and args.quiet_ok:
                    pass
                else:
                    tag = "(cache)" if cached else ""
                    print(f"  {mark} [{r.num}] {res['verdict']} {tag}")
                    print(f"       記事: {r.raw[:160]}")
                    if res.get("evidence"):
                        print(f"       PubMed: {res['evidence']}")
                    if res.get("note"):
                        print(f"       備考: {res['note']}")

                rows.append({
                    "file": rel(path), "ref_no": r.num, "verdict": res["verdict"],
                    "authors": r.authors, "title": r.title, "bib": r.bib_str(),
                    "pmid": res.get("pmid", ""), "evidence": res.get("evidence", ""),
                    "note": res.get("note", ""), "raw": r.raw,
                })
    finally:
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "file", "ref_no", "verdict", "authors", "title", "bib",
                "pmid", "evidence", "note", "raw"])
            w.writeheader()
            w.writerows(rows)
        print(f"\nCSV: {out_path}")

    print("\n" + "=" * 60)
    print(f"対象記事 {len(targets)}本 / 抽出文献 {n_extracted}件")
    if missing_refs_files:
        print(f"参照論文セクションが空の記事: {len(missing_refs_files)}本")
    if args.dry_run:
        print("dry-run のため判定は行っていません。")
        return 0

    print(f"  OK {totals[V_OK]} / 書誌誤り {totals[V_BIB]} / "
          f"合成疑い {totals[V_SYNTH]} / 不在 {totals[V_MISSING]} / 対象外 {totals[V_OUT]}")
    if pm:
        print(f"  E-utilities 呼び出し {pm.calls}回")
    if totals[V_OUT]:
        print("  ※ 対象外の文献は発行元URLを記事内コメントか作業記録に残すこと")

    ng = totals[V_SYNTH] + totals[V_MISSING]
    if ng:
        print(f"\n❌ ゲート不合格: 合成疑い・不在が {ng}件。公開（git commit）前に修正すること。")
        return 1
    print("\n✅ ゲート合格: 合成疑い・不在は0件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
