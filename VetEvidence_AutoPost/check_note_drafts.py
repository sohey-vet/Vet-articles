# -*- coding: utf-8 -*-
"""note.com の下書き一覧を実際に開き、直近の月水金に公開すべき下書きが
存在するかを照合するチェッカー（読み取り専用・何もクリックしない）。

publish_note_daily_draft.py と同一のロジック
（schedule→ソースmd→タイトル→先頭15文字でaria-label照合）を再利用するため、
「チェッカーがOKなら12:00の自動公開も見つけられる」ことが保証される。

結果は logs/note_draft_check.json に保存され、原稿チェッカー（ガジェット）が表示する。
"""
import os
import sys
import json
import time
from datetime import date, datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import publish_note_daily_draft as P  # ソース→タイトル解決を本番と共有

from playwright.sync_api import sync_playwright

CACHE_FILE = os.path.join(SCRIPT_DIR, "logs", "note_draft_check.json")
MISSED_DIR = os.path.join(SCRIPT_DIR, "logs", "missed_alerted")
DESKTOP = r"C:\Users\souhe\Desktop"  # run_daily.py の DESKTOP と同一の場所

# 過去日も照合対象にする範囲。過去日を results に載せないと next_week_dashboard の
# note_state() が「未照合」(WIP)にしか倒れず、既に実装済みの
# 「過去日なのに公開も下書きも無い → MISS 未投稿の疑い！」が到達不能になる。
PAST_CHECK_DAYS = 7
# デスクトップへ「未投稿の疑い」を出す範囲。丸1日の未投稿を翌日に気づくのが目的。
MISSED_ALERT_DAYS = 2


def expected_titles():
    """直近1週間の過去日〜翌週日曜の月水金について {date: タイトル or None} を返す。

    過去日を含めるのは「丸1日投稿されなかった日」を検知するため（PCが終日OFFだと
    run_daily.py 側の失敗警告は一度も走らず無音になる）。月水金のみが対象なので
    増えるのは2〜3件で、照合はラベル文字列の突き合わせなのでコストは変わらない。
    """
    today = date.today()
    end = today + timedelta(days=(6 - today.weekday()) + 7)
    out = {}
    d = today - timedelta(days=PAST_CHECK_DAYS)
    while d <= end:
        if d.weekday() in (0, 2, 4):
            title, note = None, ""
            src = P.load_todays_post_source(d)
            if not src:
                note = "スケジュールにソース無し"
            else:
                md = P.find_original_md_file(src)
                if not md:
                    note = "ソースmdが見つからない"
                else:
                    title = P.get_title_from_md(md)
            out[d.isoformat()] = {"title": title, "note": note}
        d += timedelta(days=1)
    return out


def scrape_labels(page, status):
    """note.com の記事一覧を status 別に読み取り、aria-label を集める。
    status: 'draft'（下書き） または 'published'（公開済み）。読み取り専用。"""
    page.goto(f"https://note.com/notes?status={status}", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    labels = set()
    for _ in range(8):
        for lb in page.evaluate(
            """() => Array.from(document.querySelectorAll('a[aria-label],button[aria-label]'))
                        .map(e => e.getAttribute('aria-label'))"""):
            if lb:
                labels.add(lb)
        page.evaluate("window.scrollBy(0, 600)")
        time.sleep(0.8)
    return sorted(labels)


def scrape_draft_labels(page):
    """後方互換: 下書きのみ。make_note_drafts など他スクリプトからも利用。"""
    return scrape_labels(page, "draft")


def alert_missed_posts(results, today):
    """直近 MISSED_ALERT_DAYS 日以内の過去日で公開も下書きも無い＝「丸1日未投稿の疑い」を
    デスクトップの警告ファイルにする（--cache-only＝ディスパッチャ経路専用）。

    run_daily.py の desktop_alert() は「投稿を試みて失敗した」ときだけ出るので、
    PCが終日OFF＝ステップが1つも走らなかった日は失敗リストが空で完全に無音になる。
    タスクスケジューラで確実に走るこの経路から補完する（ダッシュボード未起動でも届く）。

    ファイル名を【投稿エラー】と別名にするのは、未投稿は「投稿の失敗」ではなく
    「投稿の機会そのものが無かった」状態であり、誤称すると原因究明を誤らせるため。
    logs/missed_alerted/ のマーカーで同じ日付は一度しか書かない（冪等）。
    戻り値: 今回新しく警告を作った日付のリスト。
    """
    made = []
    for ds, r in sorted(results.items()):
        if r.get("state") != "missing":
            continue
        d = datetime.fromisoformat(ds).date()
        if not (today - timedelta(days=MISSED_ALERT_DAYS) <= d < today):
            continue
        marker = os.path.join(MISSED_DIR, f"{ds}.txt")
        if os.path.exists(marker):
            print(f"  ⏭  {ds}: 未投稿の疑いは既に通知済みです")
            continue
        wd = "月火水木金土日"[d.weekday()]
        path = os.path.join(DESKTOP, f"【未投稿の疑い】{ds}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"=== note未投稿の疑い: {ds}（{wd}）===\n\n")
            f.write(f"記事: {r.get('title') or '(タイトル不明)'}\n\n")
            f.write("この日のnote投稿が、公開済み・下書きのどちらにも見つかりませんでした。\n")
            f.write("PCが終日起動しておらず、予約投稿が一度も走らなかった可能性があります。\n")
            f.write("（投稿を試みて失敗した場合は【投稿エラー】ファイルが出ます。\n")
            f.write("  そちらが無い＝試行そのものが無かった、という切り分けになります）\n\n")
            f.write("▼ 目視確認\n")
            f.write("  公開済み: https://note.com/notes?status=published\n")
            f.write("  下書き  : https://note.com/notes?status=draft\n\n")
            f.write("▼ 復旧（この日の分を追い付き実行する）\n")
            f.write(f"  cd {SCRIPT_DIR}\n")
            f.write(f'  python run_daily.py --now "{ds} 12:00"\n')
            f.write(f"  ※ logs/attempted/{ds}_note.txt が残っている場合は削除してから実行\n")
            f.write("  ※ note公開は publish 側で冪等化済み（公開済みなら何もしない）\n\n")
            f.write(f"検知: check_note_drafts.py --cache-only / "
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        os.makedirs(MISSED_DIR, exist_ok=True)
        with open(marker, "w", encoding="utf-8") as f:
            f.write(datetime.now().isoformat(timespec="seconds") + "\n")
        made.append(ds)
        print(f"  🚨 {ds}: 未投稿の疑い → デスクトップに警告を作成しました（{path}）")
    return made


def main():
    expected = expected_titles()
    print("=" * 56)
    print(f" note.com 下書き照合  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 56)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=P.SESSION_DIR,
            channel="msedge",
            headless=False,  # 本番の公開スクリプトと同一条件
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        draft_labels = scrape_labels(page, "draft")
        published_labels = scrape_labels(page, "published")  # 公開済みも照合（12:00公開後の誤検知を防ぐ）
        browser.close()

    today = date.today()
    results = {}
    for ds, info in expected.items():
        title = info["title"]
        if not title:
            results[ds] = {"title": None, "found": False, "published": False,
                           "state": "unknown", "note": info["note"]}
            print(f"  ⚠  {ds}: 照合不能（{info['note']}）")
            continue
        key = title[:15].strip()  # publish_existing_draft と同じ照合キー
        is_draft = any(key in lb for lb in draft_labels)
        is_published = any(key in lb for lb in published_labels)
        # 状態の優先順位: 公開済み > 下書きあり > 無し
        state = "published" if is_published else ("draft" if is_draft else "missing")
        results[ds] = {"title": title, "found": is_draft, "published": is_published,
                       "state": state, "note": ""}
        if state == "published":
            mark, msg = "🎉", "公開済み（投稿成功）"
        elif state == "draft":
            mark, msg = "✅", "下書きあり"
        else:
            # 過去日で無い＝投稿されなかった疑い。未来日＝これから作ればよい。
            mark = "⚠" if datetime.fromisoformat(ds).date() < today else "❌"
            msg = ("公開も下書きも無し（未投稿の疑い）" if datetime.fromisoformat(ds).date() < today
                   else "下書き無し！ ③Noteバッチで作成を")
        print(f"  {mark} {ds}: 「{title}」 → {msg}")

    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"checked_at": datetime.now().isoformat(timespec="seconds"),
                   "results": results, "draft_labels": draft_labels,
                   "published_labels": published_labels}, f, ensure_ascii=False, indent=1)
    print("-" * 56)
    print(f" 結果を保存しました: {CACHE_FILE}")
    # 要対応＝「未来の月水金なのに下書きも公開も無い」ものだけ。公開済み・下書き有はOK。
    actionable = [ds for ds, r in results.items()
                  if r.get("state") == "missing"
                  and datetime.fromisoformat(ds).date() >= today]
    # --cache-only: キャッシュ更新だけを目的とした呼び出し（run_daily.py の note_check）。
    # 在庫不足は note_state() が MISS を返し AI Office 経由で社長ToDoボードへ正しい文言で
    # 届くので、ここで終了コード2を返すのは冗長。ディスパッチャは非0を投稿失敗と見なして
    # 【投稿エラー】ファイルを作るため、在庫不足が「投稿エラー」と誤称されるのを防ぐ。
    # 画面出力（⚠/❌ 行）はログに残したいのでそのまま出す。
    if "--cache-only" in sys.argv:
        # 未来日の在庫不足は終了コードで鳴らさないが、過去日の「丸1日未投稿」は
        # PC終日OFF時に他のどの経路でも通知されないのでここで必ず可視化する。
        # デスクトップへ書くだけで、終了コードは 0 のまま（Eの主旨を壊さない）。
        alert_missed_posts(results, today)
        sys.exit(0)
    sys.exit(0 if not actionable else 2)


if __name__ == "__main__":
    main()
