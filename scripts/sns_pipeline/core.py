import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル用）
load_dotenv()

# Gemini APIの初期化（環境変数から取得）
# 実行前に環境変数 GEMINI_API_KEY が設定されていることを前提とします
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # ユーザー指示により、gemini-3.1-pro-preview または gemini-pro を使用（デフォルトは安定版gemini-2.5-pro）
    model_name = "gemini-3.1-pro-preview"
    model = genai.GenerativeModel(model_name)
else:
    model = None

def extract_article_info(md_filepath):
    """
    Markdownファイルからタイトル、ジャンル（カテゴリ）、タグ、本文を抽出する
    """
    if not os.path.exists(md_filepath):
        raise FileNotFoundError(f"ファイルが見つかりません: {md_filepath}")

    with open(md_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # ファイル拡張子に応じた抽出ロジック
    ext = os.path.splitext(md_filepath)[1].lower()
    
    title = os.path.basename(md_filepath).replace(ext, '')
    tags = []
    
    if ext == '.html':
        # HTMLの場合の抽出（タイトルとタグ）
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            # タグ類を除去してプレーンテキスト化
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        
        # 簡易的なタグ抽出（HTMLの本文や特定のmeta要素から推測）
        tags_match = re.search(r'data-tags="([^"]+)"', content)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(',')]
            
        # 本文のタグを除去してプレーンテキストに近い状態にする（Geminiが読みやすくするため）
        # scriptやstyleタグの中身を削除
        text_content = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content, flags=re.IGNORECASE | re.DOTALL)
        # その他のHTMLタグを削除
        text_content = re.sub(r'<[^>]+>', ' ', text_content)
        # 連続する空白や改行を整理
        content = re.sub(r'\s+', ' ', text_content).strip()
        
    else:
        # Markdown（既存ロジック）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            
        tags_match = re.search(r'<!--\s*tags:\s*(.+?)\s*-->', content)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(',')]
    
    # カテゴリ（ディレクトリ名から推測）
    # 例: topics/救急/低血糖の緊急管理.md -> 救急
    category = "その他"
    parts = md_filepath.split(os.sep)
    if 'topics' in parts:
        try:
            category_idx = parts.index('topics') + 1
            if category_idx < len(parts):
                category = parts[category_idx]
        except ValueError:
            pass

    # 対象動物の推測（タイトルやカテゴリ、タグから）
    target_animal = ""
    if "犬" in title or "犬" in category or "犬" in tags:
        target_animal = "犬"
    elif "猫" in title or "猫" in category or "猫" in tags:
        target_animal = "猫"
    elif "犬猫" in title or "犬猫" in category or "犬猫" in tags:
        target_animal = "犬・猫"

    return {
        "title": title,
        "category": category,
        "tags": tags,
        "target_animal": target_animal,
        "content": content
    }

def call_gemini(prompt):
    """
    Gemini APIを呼び出してテキストを生成する
    """
    if not model:
        return "[エラー] GEMINI_API_KEYが設定されていないため、AI生成はスキップされました。"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini API呼び出しエラー]: {str(e)}"
