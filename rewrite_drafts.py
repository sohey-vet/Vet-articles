import os
import glob
import re
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv(r"C:\Users\souhe\Desktop\論文まとめ\.env")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

DRAFTS_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
SOURCE_DIR = r"C:\Users\souhe\Desktop\論文まとめ"

# Create a prompt text
PROMPT_TEMPLATE = """
以下の獣医学関連の記事内容を踏まえ、X（Twitter）用の投稿文テキスト「パターン1」と「パターン2」を作成してください。
【厳格な文字数ルール】
- パターン1は、「タイトル」＋「❌ 昔: {昔の常識}」＋「✅ 今: {現在推奨される内容}」の文字数の合計が【135文字以内】であること。
- パターン2は、「タイトル」＋「{本文}」の文字数の合計が【135文字以内】であること。
- ※全角・半角に関わらず1文字としてカウント（Pythonのlen()相当）します。スペースも1文字です。
- 文字数に余裕を持たせ、例えば110〜125文字程度を狙うと「135文字超過エラー」になりにくいです。
- 医学的な正確性（禁忌や推奨事項など）は絶対に省略せず、冗長な言い回しのみを削ってください。

以下のJSONフォーマットで出力してください。Markdownのコードブロック(```jsonなど)は不要です。必ずパース可能なJSONのみを出力してください。
{
  "pattern1": {
    "title": "犬猫の中毒 ─ 誤食時の催吐処置",
    "mukashi": "誤食時はオキシドール等で吐かせる。成功すれば安心。",
    "ima": "オキシドールでの催吐は禁忌。犬はトラネキサム酸IV等を使用。吸収阻害のため活性炭投与も考慮する。"
  },
  "pattern2": {
    "title": "犬猫の中毒 ─ 催吐処置と初期対応",
    "honbun": "オキシドールでの催吐は禁忌。犬はトラネキサム酸IV等を使用。胃内容物回収率は低いため、残存毒素への対策として活性炭の投与を考慮します。"
  }
}

【記事の本文】
"""

def generate_short_texts(source_text, retry_count=3):
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    
    for attempt in range(retry_count):
        try:
            response = model.generate_content(PROMPT_TEMPLATE + source_text)
            data = json.loads(response.text)
            
            p1 = data['pattern1']
            p2 = data['pattern2']
            
            p1_len = len(p1['title']) + len("❌ 昔: ") + len(p1['mukashi']) + len("\n✅ 今: ") + len(p1['ima']) + 1 # +1 for \n after title
            p2_len = len(p2['title']) + len(p2['honbun']) + 1 # +1 for \n after title
            
            if p1_len <= 135 and p2_len <= 135:
                # Return formatted texts
                p1_text = f"{p1['title']}\n\n❌ 昔: {p1['mukashi']}\n✅ 今: {p1['ima']}"
                p2_text = f"{p2['title']}\n\n{p2['honbun']}"
                return p1_text, p2_text
            else:
                print(f"  [Attempt {attempt+1}] 文字数超過: P1={p1_len}, P2={p2_len}。再試行します...")
                # We could add the feedback to the next prompt, but genai is stateless unless we use chat.
                # Just waiting and retrying usually gives variation, but let's be explicit.
                time.sleep(1)
        except Exception as e:
            print(f"  APIエラーまたはJSONパースエラー: {e}")
            time.sleep(2)
            
    # Fallback to last generated if all failed
    print("  警告: リトライ上限に達しましたが、135文字の制約を満たせませんでした。最後の出力を採用します。")
    try:
        if 'p1' in locals():
            p1_text = f"{p1['title']}\n\n❌ 昔: {p1['mukashi']}\n✅ 今: {p1['ima']}"
            p2_text = f"{p2['title']}\n\n{p2['honbun']}"
            return p1_text, p2_text
    except Exception:
        pass
    return None, None

def process_file(draft_filepath):
    print(f"Processing: {os.path.basename(os.path.dirname(draft_filepath))}/{os.path.basename(draft_filepath)}")
    with open(draft_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract source file path
    match = re.search(r"元ファイル: (topics\\[^\n]+\.md)", content)
    if not match:
        # try without md
        match = re.search(r"元ファイル: (topics\\[^\n]+)", content)
        if not match:
            print("  [エラー] 元ファイルのパスが見つかりません。")
            return False
            
    source_md_rel = match.group(1).strip()
    source_md_path = os.path.join(SOURCE_DIR, source_md_rel)
    source_html_path = source_md_path.replace('.md', '.html')
    
    source_path = source_md_path # Prefer MD for LLM, less tokens and easier to read.
    if not os.path.exists(source_path):
        if os.path.exists(source_html_path):
            source_path = source_html_path
        else:
            print(f"  [エラー] 大元データが存在しません: {source_md_path}")
            return False
            
    print(f"  ソース読み込み: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        source_text = f.read()

    # We need to extract the existing Pattern 1 and 2 blocks so we can preserve tags.
    # Pattern 1
    # Match everything between "### パターン1:" and "```"
    p1_block_match = re.search(r"(### パターン1:.*?```text)(.*?)(```)", content, re.DOTALL)
    p2_block_match = re.search(r"(### パターン2:.*?```text)(.*?)(```)", content, re.DOTALL)
    
    if not p1_block_match or not p2_block_match:
        print("  [エラー] パターン1または2のブロックが見つかりません。")
        return False
        
    p1_inner = p1_block_match.group(2)
    p2_inner = p2_block_match.group(2)
    
    # Extract Hashtags and Reference (📄 根拠: ...)
    p1_konkyo_match = re.search(r"(📄 根拠:.*?)(?=\n|$)", p1_inner)
    p1_tags_match = re.search(r"(#\w+.*)", p1_inner)
    
    p2_note_match = re.search(r"(詳しくは Note で.*?)", p2_inner)
    p2_tags_match = re.search(r"(#\w+.*)", p2_inner)
    
    p1_konkyo = p1_konkyo_match.group(1) if p1_konkyo_match else "📄 根拠: エビデンス文献"
    p1_tags = p1_tags_match.group(1) if p1_tags_match else "#獣医 #動物救急"
    
    p2_note = p2_note_match.group(1) if p2_note_match else "詳しくは Note で（プロフにリンク）"
    p2_tags = p2_tags_match.group(1) if p2_tags_match else "#獣医 #動物救急"
    
    print("  AIによるテキスト短縮を要求しています...")
    p1_new_text, p2_new_text = generate_short_texts(source_text)
    
    if not p1_new_text:
         return False
         
    # Reconstruct blocks
    p1_final = f"\n{p1_new_text}\n\n{p1_konkyo}\n\n{p1_tags}\n"
    p2_final = f"\n{p2_new_text}\n\n{p2_note}\n\n{p2_tags}\n"
    
    # Replace in original content
    # re.sub needs carefully escaped strings or string slicing.
    new_content = content[:p1_block_match.start(2)] + p1_final + content[p1_block_match.end(2):]
    
    # recalculate the match index for p2 because content length changed
    # Better to just use replace() if p2_inner is totally unique
    new_content = new_content.replace(p2_inner, p2_final)
    
    with open(draft_filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("  [完了] アップデートして保存しました。")
    return True

if __name__ == "__main__":
    md_files = glob.glob(os.path.join(DRAFTS_DIR, "**", "sns_all_drafts.md"), recursive=True)
    print(f"Total files found: {len(md_files)}")
    
    success_count = 0
    # TEST RUN: ONLY 5 FILES
    for md_file in md_files[:5]:
        if process_file(md_file):
            success_count += 1
            
    print(f"\nテスト実行完了: {success_count}/5 成功")
