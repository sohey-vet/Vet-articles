# -*- coding: utf-8 -*-
"""夜Threads/Substack/昼Threads(来週分)の「AIが下書きし終えて、人間のレビュー待ち」
アイテムを検知し、新規分だけ秘書経由で社長ToDoボードへ1回通知する。

run_daily.py の12:00ブロック最後のステップとして毎日実行される想定。
- 対象: Owner_Track配下の `_未完_*` ファイルのうち「テーマ未定」を含まない
  （= draft_owner_articles.py が本文まで書き終えたが、まだ `_未完_` を外していない）もの。
  昼Threadsの「来週のThreads修正用.md」も対象に含める。
- 重複通知防止: logs/owner_review_notify_state.json に通知済みキーを保持し、
  前回から増えた分だけを対象にする（確定済み=ファイルが無くなった分は自然に対象から外れる）。
- 通知先: 秘書の唯一の書き込み経路 dispatcher.report_to_secretary()（社長ToDoボードの
  「🔴 社長にしかできないこと」セクションへ1行追記するだけ・他は一切触らない）。
"""
import os
import sys
import glob
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OWNER_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "Owner_Track")
STATE_PATH = os.path.join(SCRIPT_DIR, "logs", "owner_review_notify_state.json")
NEXT_WEEK_THREADS_FILE = os.path.join(SCRIPT_DIR, "来週のThreads修正用.md")

AI_OFFICE_DIR = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "AI_Office")
sys.path.insert(0, AI_OFFICE_DIR)

SUFFIX_LABEL = {"__threads.txt": "夜Threads", "__substack.md": "Substack"}

# ボード側の二重防御用・固定の安定接頭辞（件数などの可変部分を含めない）。
# レビュー待ち通知は「ボードに常時1行あれば十分」という設計のため、件数が
# 変わっても新しい行を追加しない（＝この接頭辞そのものを dedup_key にする）。
NOTIFY_DEDUP_PREFIX = "【AI Office/レビュー待ち】"


def _load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return set(json.load(f).get("notified", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def _save_state(notified):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"notified": sorted(notified)}, f, ensure_ascii=False, indent=1)


def find_owner_review_items():
    """夜Threads/Substackの「本文まで書けたがまだ確定していない」ファイル名一覧"""
    out = []
    for suffix, label in SUFFIX_LABEL.items():
        for p in sorted(glob.glob(os.path.join(OWNER_DIR, f"_未完_*{suffix}"))):
            name = os.path.basename(p)
            if "テーマ未定" in name:
                continue  # まだAIが書いていない未着手プレースホルダ
            out.append((name, label))
    return out


def find_next_week_threads_item():
    """昼Threadsの来週分準備ファイル。存在すれば (キー, 見出し行) を返す"""
    if not os.path.exists(NEXT_WEEK_THREADS_FILE):
        return None
    try:
        with open(NEXT_WEEK_THREADS_FILE, encoding="utf-8") as f:
            first_line = f.readline().strip()
    except OSError:
        return None
    return f"threads_next_week::{first_line}", first_line


def main():
    notified = _load_state()
    current_keys = set()
    new_owner_items = []
    new_next_week = None

    for name, label in find_owner_review_items():
        key = f"owner::{name}"
        current_keys.add(key)
        if key not in notified:
            new_owner_items.append((name, label))

    nw = find_next_week_threads_item()
    if nw:
        key, first_line = nw
        current_keys.add(key)
        if key not in notified:
            new_next_week = first_line

    if not new_owner_items and not new_next_week:
        print("新規のレビュー待ちアイテムはありません。")
        return 0

    lines = []
    if new_owner_items:
        by_label = {}
        for name, label in new_owner_items:
            by_label.setdefault(label, []).append(name)
        parts = [f"{label}{len(names)}件" for label, names in by_label.items()]
        lines.append("・".join(parts) + "の下書きができました。owner_draft_editor.pywでレビュー・確定してください。")
    if new_next_week:
        lines.append("昼Threads来週分の準備ができました（来週のThreads修正用.md）。①バッチでレビューできます。")

    # message 本体（件数・ラベルの組み合わせで内容が変わる部分）の先頭に、
    # 固定の安定接頭辞 NOTIFY_DEDUP_PREFIX を付ける。
    # - 状態ファイル（logs/owner_review_notify_state.json）は「新しいアイテムに
    #   ついて1回だけ通知する」役割。
    # - この接頭辞 dedup は、状態ファイルが壊れる/リセットされる・下書きファイルが
    #   リネームされて別キー扱いになる、といった失敗時でもボードが二重にならない
    #   ための第二の防御（＝件数が変わっても行を増やさず、ボードには常時最大1行）。
    # - 接頭辞を付けることで remove_secretary_reports(NOTIFY_DEDUP_PREFIX) でも
    #   この行を消せる（外部から解消済みとして片付けられる）。
    message = NOTIFY_DEDUP_PREFIX + " / ".join(lines)

    try:
        from dispatcher import report_to_secretary
        report_to_secretary(message, dedup_key=NOTIFY_DEDUP_PREFIX)
    except Exception as e:
        print(f"❌ 秘書への通知に失敗しました: {e}")
        return 1

    print(f"社長ToDoボードへ通知しました: {message}")
    _save_state(notified | current_keys)
    return 0


if __name__ == "__main__":
    sys.exit(main())
