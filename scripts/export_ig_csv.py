import os
import re
import csv
import glob

def extract_instagram_slides_to_csv(md_path, csv_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the Instagram section
    ig_section_matches = re.finditer(r'## 🟣 Instagram用.*?```text(.*?)```', content, flags=re.DOTALL)
    ig_text = ""
    for m in ig_section_matches:
        ig_text = m.group(1).strip()
        
    if not ig_text:
        # Fallback if the format is slightly different
        ig_section_matches = re.finditer(r'=== Instagram スライド台本 ===(.*?)=== キャプション', content, flags=re.DOTALL)
        for m in ig_section_matches:
            ig_text = m.group(1).strip()

    if not ig_text:
        print(f"No Instagram section found in {md_path}")
        return False

    # Regex to match each slide
    slide_pattern = re.compile(r'\[(\d+)枚目:\s*(.*?)\]\n(.*?)(?=\n\[\d+枚目|\Z)', re.DOTALL)
    slides = slide_pattern.findall(ig_text)

    if not slides:
        print(f"Could not parse individual slides in {md_path}")
        return False

    headers = ['スライド番号', '役割', 'テキスト']
    rows = []
    
    for slide_num, role, slide_text in slides:
        clean_text = slide_text.strip()
        rows.append([f"{slide_num}枚目", role.strip(), clean_text])

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print(f"Successfully exported CSV with {len(rows)} slides to {csv_path}")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Process a specific file
        md_file = sys.argv[1]
        csv_out = os.path.splitext(md_file)[0] + "_ig_carousel_data.csv"
        extract_instagram_slides_to_csv(md_file, csv_out)
    else:
        # Process all VetEvidence_SNS_Drafts
        drafts_dir = os.path.join(os.path.expanduser("~"), "Desktop", "VetEvidence_SNS_Drafts")
        if not os.path.exists(drafts_dir):
            print(f"Drafts directory not found: {drafts_dir}")
            sys.exit(1)
            
        md_files = glob.glob(os.path.join(drafts_dir, "*", "sns_all_drafts.md"))
        count = 0
        for md_file in md_files:
            dir_name = os.path.dirname(md_file)
            csv_out = os.path.join(dir_name, "ig_carousel_data.csv")
            if extract_instagram_slides_to_csv(md_file, csv_out):
                count += 1
                
        print(f"\nCompleted exporting CSVs for {count} folders.")
