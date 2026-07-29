"""PawMedical 予約投稿ディスパッチャ（唯一のスケジューラ入口）

タスクスケジューラの単一タスク "PawMedical_AutoPost" から起動され、
「今日・今の時刻までに実行すべき投稿ステップ」を判断して順に実行する。

旧構成（4タスク + bat連鎖 + ThreadsBot自己再登録PS1ペア）を全て置き換える。
  - 12:00 毎日      : X / Threads(日曜以外) / Note(月水金)   … 旧 2_Run_Daily_Post.bat
  - 20:30 月水金    : 夜の部 Threads + Substack              … 旧 run_owner_evening 経由タスク
  - 日曜 ローテ時刻 : 診察室裏トーク（4週ローテ）            … 旧 ThreadsBot stager/post_now.ps1

設計原則（2026-07-05 無言失敗事故の教訓）:
  1. 各ステップは「試行済みマーカー」(logs/attempted/) で二重実行を防ぐ。
     PCがスリープしていてトリガーを逃しても、次の起動時に同日分を自動で追い付く。
  2. 失敗したステップは自動再試行しない（二重投稿リスク回避）。
     代わりにデスクトップへ【投稿エラー】ファイルを置いて必ず可視化する。
     例外: note は publish_note_daily_draft.py の「公開済みチェック」で冪等化済み
     （再実行しても公開済みなら何もせず exit 0）なので、前回FAIL時に限り
     同日1回だけ再試行する。マーカーのFAIL行数で再試行回数を判定し、2回目以降は打ち切る。
  3. 「成功」は子スクリプトの exit code に基づく。Threads単発投稿は
     auto_post_threads.py 側でプロフィール照合済みのため exit 0 = 実在確認済み。
  4. 日曜ローテの式は extract_weekly_threads.sunday_talk_index を唯一の情報源とする
     （PS1側とPython側の二重管理を廃止）。

手動テスト:
  python run_daily.py --dry-run --now "2026-07-12 20:30"
"""
import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime, time as dtime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
ATTEMPT_DIR = os.path.join(LOG_DIR, "attempted")
THREADSBOT_DIR = r"C:\Users\souhe\Documents\ThreadsBot"
DESKTOP = r"C:\Users\souhe\Desktop"
STEP_TIMEOUT_SEC = 15 * 60  # Playwrightが固まった場合の保険

# 日曜「診察室裏トーク」ローテの式は extract_weekly_threads を唯一の情報源にする
sys.path.insert(0, SCRIPT_DIR)
from extract_weekly_threads import sunday_talk_index, SUNDAY_NAMES

# 週ごとの最適投稿時刻（旧 schedule_today.ps1 の $times を移設。管理はこの1箇所のみ）
SUNDAY_TIMES = {1: dtime(20, 30), 2: dtime(8, 0), 3: dtime(21, 0), 4: dtime(8, 0)}

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ATTEMPT_DIR, exist_ok=True)
handlers = [logging.FileHandler(
    os.path.join(LOG_DIR, f"dispatch_{datetime.now().strftime('%Y%m')}.log"),
    encoding="utf-8")]
if sys.stdout is not None:  # pythonw.exe起動時はコンソールが無い
    handlers.append(logging.StreamHandler())
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s", handlers=handlers)
logger = logging.getLogger(__name__)

PY = sys.executable


def flag_path(date_str, step):
    return os.path.join(ATTEMPT_DIR, f"{date_str}_{step}.txt")


def already_attempted(date_str, step):
    return os.path.exists(flag_path(date_str, step))


def note_retry_allowed(date_str):
    """note ステップに限り、同日1回だけの再試行を許可するか判定する。
    許可条件（すべて満たす）:
      - マーカーが存在する
      - まだ成功(OK)していない
      - FAIL 行がちょうど1行（=まだ一度も再試行していない。2行以上なら打ち切り）
    note は publish 側の公開済みチェックで冪等化済みのため、再実行しても二重投稿にならない。
    他ステップ(x/threads/owner_*/sunday_talk)は対象外（従来どおり再試行しない）。"""
    path = flag_path(date_str, "note")
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
    except OSError:
        return False
    if any("OK" in ln for ln in lines):
        return False  # 既に成功済み
    fail_lines = [ln for ln in lines if "FAIL" in ln]
    return len(fail_lines) == 1


def mark_attempted(date_str, step, result):
    # note は再試行のため FAIL 履歴を追記する（FAIL 行数で再試行回数を判定するため）。
    # 他ステップは従来どおり上書き（"w"）。
    mode = "a" if (step == "note" and os.path.exists(flag_path(date_str, step))) else "w"
    with open(flag_path(date_str, step), mode, encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {result}\n")


def desktop_alert(date_str, lines):
    """失敗を必ず目に入る形で残す（無言失敗の根絶）"""
    path = os.path.join(DESKTOP, f"【投稿エラー】{date_str}.txt")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"--- {datetime.now().strftime('%H:%M:%S')} ---\n")
        for line in lines:
            f.write(line + "\n")
        f.write("詳細ログ: VetEvidence_AutoPost/logs/\n\n")
    logger.error(f"デスクトップに警告ファイルを作成: {path}")


def run_step(date_str, step, cmd, dry_run):
    """1ステップ実行。戻り値: True=成功 / False=失敗 / None=スキップ(試行済み)"""
    if already_attempted(date_str, step):
        # 例外: note は冪等化済み（公開済みチェック）なので、前回FAIL時のみ同日1回だけ再試行する
        if step == "note" and note_retry_allowed(date_str):
            logger.info(f"🔁 {step}: 前回FAIL・冪等化済みのため同日1回だけ再試行します")
        else:
            logger.info(f"⏭  {step}: 本日試行済みのためスキップ")
            return None
    if dry_run:
        logger.info(f"🔸 [DRY] {step}: {' '.join(cmd)}")
        return True
    logger.info(f"▶  {step}: {' '.join(cmd)}")
    env = dict(os.environ, PYTHONUTF8="1")
    try:
        proc = subprocess.run(cmd, cwd=SCRIPT_DIR, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=STEP_TIMEOUT_SEC)
        ok = proc.returncode == 0
        tail = proc.stdout.decode("utf-8", errors="replace").strip().splitlines()[-3:]
        for line in tail:
            logger.info(f"    | {line}")
    except subprocess.TimeoutExpired:
        ok = False
        logger.error(f"    | {STEP_TIMEOUT_SEC}秒でタイムアウト。プロセスを終了しました。")
    mark_attempted(date_str, step, "OK" if ok else "FAIL")
    logger.info(f"{'✅' if ok else '❌'} {step}")
    return ok


def archive_sunday(date_str, idx, text, ok):
    """裏トークの投稿記録（旧post_now.ps1のアーカイブを踏襲・結果は正直に記録）"""
    posted_dir = os.path.join(THREADSBOT_DIR, "posted")
    os.makedirs(posted_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    result = "成功(プロフィール照合済み)" if ok else "失敗"
    with open(os.path.join(posted_dir, f"{stamp}_week{idx}.txt"), "w", encoding="utf-8") as f:
        f.write(f"=== 投稿日時: {stamp} / {SUNDAY_NAMES[idx]} (post{idx}) / 結果: {result} ===\n\n")
        f.write(text)


def due_steps(now):
    """今日この時点までに実行すべき (step名, コマンド, 説明) を時系列順に返す"""
    date_str = now.strftime("%Y-%m-%d")
    wd = now.weekday()  # 月=0 … 日=6
    steps = []

    # --- 12:00 デイリー（旧 2_Run_Daily_Post.bat と同一内容・同一順序） ---
    if now.time() >= dtime(12, 0):
        steps.append(("x", [PY, "auto_post_x.py"], "X 12:00"))
        if wd != 6:  # 日曜のThreadsは裏トークに一本化済み
            steps.append(("threads", [PY, "auto_post_threads.py"], "Threads 12:00"))
        # Note下書き在庫の維持（曜日を問わず毎日・不足分のみ作成される冪等ツール）
        steps.append(("note_stock", [PY, "make_note_drafts.py", "--upcoming", "6"],
                      "Note在庫確保（翌週末まで）"))
        if wd in (0, 2, 4):
            steps.append(("note", [PY, "publish_note_daily_draft.py"], "Note 12:00"))
        # note.com実照合キャッシュ(logs/note_draft_check.json)の更新。読み取り専用。
        # 月水金だけにすると日曜〜火曜でキャッシュが24時間の有効期限を超えて失効し、
        # AI Office側が全枠を「未照合」と誤判定して誤報を出す（7/29誤報事故）。毎日更新する。
        # --cache-only は「在庫不足でも exit 0」。在庫不足はAI Office側のMISS報告で
        # ボードに届くため、ここで非0を返すと投稿は成功しているのに【投稿エラー】と誤称される。
        steps.append(("note_check", [PY, "check_note_drafts.py", "--cache-only"],
                      "Note照合キャッシュ更新"))

        # 夜Threads/Substack在庫の維持（曜日を問わず毎日・不足分のみテンプレ作成→AI下書き）
        steps.append(("owner_threads_template",
                      [PY, "make_owner_templates.py", "--only", "threads", "--no-open"],
                      "夜Threadsテンプレ確保"))
        steps.append(("owner_threads_draft",
                      [PY, "draft_owner_articles.py", "--only", "threads", "--no-open"],
                      "夜Threads下書き生成"))
        steps.append(("owner_substack_template",
                      [PY, "make_owner_templates.py", "--only", "substack", "--no-open"],
                      "Substackテンプレ確保"))
        steps.append(("owner_substack_draft",
                      [PY, "draft_owner_articles.py", "--only", "substack", "--no-open"],
                      "Substack下書き生成"))
        # 昼Threads来週分の前倒し準備（非対話モード・メモ帳は開かない）
        steps.append(("threads_daytime_stock",
                      [PY, "extract_weekly_threads.py", "--prepare-next-week"],
                      "昼Threads来週分準備"))
        # 新規に貯まった下書きがあれば秘書経由で社長ToDoボードへレビュー依頼を1回だけ通知
        steps.append(("owner_review_notify",
                      [PY, "notify_owner_review_queue.py"],
                      "レビュー待ち通知"))

    # --- 20:30 月水金 夜の部（Threads/Substackを個別ステップ化し半端な再実行を防ぐ） ---
    if wd in (0, 2, 4) and now.time() >= dtime(20, 30):
        # --date を明示的に渡し、run_owner_evening.py が実行時刻ではなく
        # ディスパッチ対象日の原稿を確実に検出できるようにする。
        # 通常運転では date_str == 当日なので子側のデフォルト(datetime.now().date())と
        # 同値であり挙動は変わらない。--now で過去日を復旧実行する場合のみ効く。
        steps.append(("owner_threads",
                      [PY, "run_owner_evening.py", "--threads-only", "--date", date_str],
                      "夜の部Threads 20:30"))
        steps.append(("owner_substack",
                      [PY, "run_owner_evening.py", "--substack-only", "--date", date_str],
                      "夜の部Substack 20:30"))

    # --- 日曜 診察室裏トーク（4週ローテ・週の最適時刻） ---
    if wd == 6:
        idx = sunday_talk_index(now.date())
        if now.time() >= SUNDAY_TIMES[idx]:
            post_file = os.path.join(THREADSBOT_DIR, f"post{idx}.txt")
            steps.append((f"sunday_talk",
                          [PY, "auto_post_threads.py", "--text-file", post_file],
                          f"{SUNDAY_NAMES[idx]} {SUNDAY_TIMES[idx].strftime('%H:%M')}"))
    return date_str, steps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="実行せず判断結果のみログに出す")
    parser.add_argument("--now", type=str, help='テスト用 "YYYY-MM-DD HH:MM"')
    args = parser.parse_args()

    now = datetime.strptime(args.now, "%Y-%m-%d %H:%M") if args.now else datetime.now()
    date_str, steps = due_steps(now)

    logger.info("=" * 50)
    logger.info(f"🗓  ディスパッチ {now.strftime('%Y-%m-%d(%a) %H:%M')}"
                + (" [DRY-RUN]" if args.dry_run else ""))
    if not steps:
        logger.info("📭 この時点で実行すべきステップはありません。")
        return

    failures = []
    for step, cmd, desc in steps:
        ok = run_step(date_str, step, cmd, args.dry_run)
        if step == "sunday_talk" and ok is not None and not args.dry_run:
            idx = sunday_talk_index(now.date())
            try:
                with open(cmd[-1], "r", encoding="utf-8") as f:
                    archive_sunday(date_str, idx, f.read(), ok)
            except OSError as e:
                logger.error(f"アーカイブ書き込み失敗: {e}")
        if ok is False:
            failures.append(f"❌ {desc} ({step}) が失敗しました。")

    if failures and not args.dry_run:
        desktop_alert(date_str, failures)
    logger.info(f"🏁 完了: {len(steps)}ステップ中 失敗{len(failures)}")


if __name__ == "__main__":
    main()
