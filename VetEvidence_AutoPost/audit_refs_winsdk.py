import os
import glob
import re
import asyncio
from bs4 import BeautifulSoup
from winsdk.windows.media.ocr import OcrEngine
from winsdk.windows.storage import StorageFile
from winsdk.windows.graphics.imaging import BitmapDecoder

async def extract_text_from_image(image_path: str):
    try:
        if not os.path.exists(image_path):
            return "NO_IMAGE"
        file = await StorageFile.get_file_from_path_async(os.path.abspath(image_path))
        stream = await file.open_async(0)
        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        
        engine = OcrEngine.try_create_from_user_profile_languages()
        if engine is None:
            return "NO_ENGINE"
        result = await engine.recognize_async(bitmap)
        text = result.text.replace(' ', '').replace('\n', '')
        
        # 参照論文数:9 or 参照論文:9 or just number near the end
        m = re.search(r'参照論[文数]+[^\d]*(\d+)', text)
        if m:
            return int(m.group(1))
        
        # fallback: find any digits at the end of the text
        m = re.search(r'(\d+)[^\d]*$', text)
        if m:
            return int(m.group(1))
            
        return f"Raw:{text}" # Return raw text if we can't extract a number
    except Exception as e:
        return f"ERROR: {e}"

async def main():
    print("Starting Audit...")
    
    index_path = r'c:\Users\souhe\Desktop\論文まとめ\index.html'
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"Failed to read index: {e}")
        return

    index_counts = {}
    for card in soup.select('.article-card'):
        title_tag = card.select_one('h3')
        if not title_tag: continue
        title = title_tag.get_text(strip=True)
        
        meta_tag = card.select_one('.meta')
        ref_count = -1
        if meta_tag:
            m = re.search(r'📄\s*(\d+)本', meta_tag.get_text())
            if m: ref_count = int(m.group(1))
        
        link = card.select_one('a')['href'] if card.select_one('a') else ""
        if link:
            fname = os.path.basename(link)
            index_counts[fname] = {'title': title, 'count': ref_count}

    folders = glob.glob(r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\*')
    mismatches = []
    
    for folder in folders:
        if not os.path.isdir(folder): continue
        if '.agents' in folder or '.vscode' in folder or 'VetEvidence_AutoPost' in folder or 'Note_' in folder or 'scripts' in folder: continue
            
        draft_md = os.path.join(folder, "sns_all_drafts.md")
        html_fname = ""
        if os.path.exists(draft_md):
            with open(draft_md, "r", encoding="utf-8", errors="ignore") as f:
                m = re.search(r'元ファイル:\s*([^\r\n]+)', f.read())
                if m:
                    path = m.group(1).strip()
                    html_fname = os.path.basename(path).replace('.md', '.html')
        
        html_path = ""
        if html_fname:
            candidates = glob.glob(fr'c:\Users\souhe\Desktop\論文まとめ\topics\*\*{html_fname}')
            if candidates: html_path = candidates[0]
            
        if not html_path or not os.path.exists(html_path):
            continue
            
        fname = os.path.basename(html_path)
            
        with open(html_path, 'r', encoding='utf-8') as f:
            fsoup = BeautifulSoup(f.read(), 'html.parser')
            
        meta_count = -1
        for item in fsoup.select('.meta-item'):
            if '📄' in item.get_text() or '参照論文' in item.get_text():
                m = re.search(r'(\d+)本', item.get_text())
                if m: meta_count = int(m.group(1))
                break
                
        refs_div = fsoup.find(id='refs')
        accordion_count = -1
        actual_count = 0
        if refs_div:
            acc_span = refs_div.find('span', string=re.compile(r'参照論文'))
            if acc_span:
                m = re.search(r'(\d+)', acc_span.get_text())
                if m: accordion_count = int(m.group(1))
            
            ol = refs_div.find('ol')
            if ol:
                actual_count = len(ol.find_all('li', recursive=False))
                
        idx_c = index_counts.get(fname, {}).get('count', -1)
        
        thumb_path = os.path.join(folder, 'note_thumbnail.png')
        ocr_result = await extract_text_from_image(thumb_path)
        
        counts = [idx_c, meta_count, accordion_count, actual_count]
        if isinstance(ocr_result, int):
            counts.append(ocr_result)
            
        valid_counts = [c for c in counts if isinstance(c, int) and c > 0]
        
        if len(set(valid_counts)) > 1:
            mismatches.append(f"[{fname}]\n Folder: {os.path.basename(folder)}\n Index.html: {idx_c}\n MetaBar: {meta_count}\n Accordion: {accordion_count}\n ActualLIs: {actual_count}\n OCR: {ocr_result}")
            print(f"Mismatch found: {fname}")

    with open(r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\ocr_audit_result.txt', 'w', encoding='utf-8') as f:
        f.write(f"Mismatches: {len(mismatches)}\n\n")
        f.write('\n\n'.join(mismatches))
    print(f"Done! {len(mismatches)} mismatches.")

if __name__ == '__main__':
    asyncio.run(main())
