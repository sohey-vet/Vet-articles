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
        file = await StorageFile.get_file_from_path_async(os.path.abspath(image_path))
        stream = await file.open_async(0)
        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        
        engine = OcrEngine.try_create_from_user_profile_languages()
        if engine is None: return -1
        result = await engine.recognize_async(bitmap)
        text = result.text.replace(' ', '').replace('\n', '')
        
        m = re.search(r'参照論[文数]+[^\d]*(\d+)', text)
        if m: return int(m.group(1))
        
        m = re.search(r'(\d+)[^\d]*$', text)
        if m: return int(m.group(1))
            
        return -1
    except Exception as e:
        return -1

async def main():
    print("Starting Bulletproof Audit...")
    
    html_files = glob.glob(r'c:\Users\souhe\Desktop\論文まとめ\topics\*\*.html')
    html_map = {}
    for h in html_files:
        html_map[os.path.basename(h).replace('.html', '')] = h

    index_path = r'c:\Users\souhe\Desktop\論文まとめ\index.html'
    index_counts = {}
    with open(index_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        for card in soup.select('.article-card'):
            meta_tag = card.select_one('.meta')
            link = card.select_one('a')
            if meta_tag and link:
                m = re.search(r'📄\s*(\d+)本', meta_tag.get_text())
                if m:
                    fname = os.path.basename(link['href']).replace('.html', '')
                    index_counts[fname] = int(m.group(1))

    thumbnails = glob.glob(r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\*\note_thumbnail.png')
    
    mismatches = []
    missing_html = []
    
    for thumb in thumbnails:
        folder = os.path.dirname(thumb)
        folder_name = os.path.basename(folder)
        
        html_path = None
        
        draft_md = os.path.join(folder, "sns_all_drafts.md")
        if os.path.exists(draft_md):
            with open(draft_md, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                m = re.search(r'元ファイル:\s*([^\r\n]+)', content)
                if m:
                    bname = os.path.basename(m.group(1).strip()).replace('.md', '')
                    if bname in html_map:
                        html_path = html_map[bname]
        
        if not html_path:
            for k, v in html_map.items():
                if k in folder_name or folder_name.endswith(k):
                    html_path = v
                    break
                    
        if not html_path:
            parts = folder_name.split('_')
            if len(parts) >= 3:
                guess = "_".join(parts[2:])
                for k, v in html_map.items():
                    if guess in k or k in guess:
                        html_path = v
                        break

        if not html_path:
            missing_html.append(folder_name)
            continue
            
        fname_base = os.path.basename(html_path).replace('.html', '')
            
        with open(html_path, 'r', encoding='utf-8') as f:
            fsoup = BeautifulSoup(f.read(), 'html.parser')
            
        meta_count = -1
        for item in fsoup.select('.meta-item'):
            if '📄' in item.get_text() or '参照論文' in item.get_text():
                m = re.search(r'(\d+)本', item.get_text())
                if m: meta_count = int(m.group(1))
                break
                
        refs_div = fsoup.find(id='refs')
        accordion_count, actual_count = -1, 0
        if refs_div:
            acc_span = refs_div.find('span', string=re.compile(r'参照論文'))
            if acc_span:
                m = re.search(r'(\d+)', acc_span.get_text())
                if m: accordion_count = int(m.group(1))
            ol = refs_div.find('ol')
            if ol:
                actual_count = len(ol.find_all('li', recursive=False))
                
        idx_c = index_counts.get(fname_base, -1)
        
        ocr_result = await extract_text_from_image(thumb)
        
        counts = [idx_c, meta_count, accordion_count, actual_count, ocr_result]
        valid_counts = [c for c in counts if c > 0]
        
        if len(set(valid_counts)) > 1:
            mismatches.append(f"[{fname_base}]\n Folder: {folder_name}\n HTML(実数): {actual_count} | OCR(サムネ): {ocr_result}\n")
            print(f"Mismatch: {folder_name} (HTML: {actual_count}, OCR: {ocr_result})")

    with open(r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\ocr_audit_result_v2.txt', 'w', encoding='utf-8') as f:
        f.write(f"Audited {len(thumbnails)} folders.\n")
        f.write(f"Mismatches: {len(mismatches)}\n")
        f.write(f"Unmatched Folders: {len(missing_html)}\n\n")
        if missing_html:
            f.write("UNIDENTIFIED FOLDERS (Failed to find HTML):\n" + "\n".join(missing_html) + "\n\n")
        f.write("MISMATCHES:\n" + '\n'.join(mismatches))
        
    print(f"Done! {len(mismatches)} mismatches, {len(missing_html)} unmatched.")

if __name__ == '__main__':
    asyncio.run(main())
