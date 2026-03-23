import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageChops

def generate_thumbnail(day, category, title, subtitle, paper_count, output_path):
    # Setup
    W, H = 1280, 670
    bg_color = (15, 23, 42)
    bg = Image.new('RGB', (W, H), bg_color)
    
    # 1. Overlay Bottom-Right Icon
    icon_path = os.path.join(r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\minimal_icons', f"{category}.jpg")
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert('RGB')
        # resize to a reasonable size, e.g., width 500
        icon_w = 600
        icon_h = int(icon_w * icon.height / icon.width)
        icon = icon.resize((icon_w, icon_h), Image.Resampling.LANCZOS)
        
        # We put it on a black canvas and use 'lighter' (screen-like)
        icon_canvas = Image.new('RGB', (W, H), (0, 0, 0))
        # paste at bottom right
        icon_canvas.paste(icon, (W - icon_w + 50, H - icon_h + 50)) 
        
        bg = ImageChops.lighter(bg, icon_canvas)

    # Prepare for drawing
    draw = ImageDraw.Draw(bg)
    
    # Fonts
    try:
        font_title = ImageFont.truetype(r'C:\Windows\Fonts\meiryob.ttc', 80)
        font_sub = ImageFont.truetype(r'C:\Windows\Fonts\meiryob.ttc', 60)
        font_pill = ImageFont.truetype(r'C:\Windows\Fonts\meiryob.ttc', 40)
        font_paper = ImageFont.truetype(r'C:\Windows\Fonts\meiryob.ttc', 48)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_pill = ImageFont.load_default()
        font_paper = ImageFont.load_default()

    # 2. Draw Top-Left Pill
    pill_color = (17, 170, 232)
    pill_x, pill_y = 60, 60
    pill_padding_x, pill_padding_y = 40, 15
    
    bbox = draw.textbbox((0, 0), category, font=font_pill)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    pill_w = text_w + pill_padding_x * 2
    pill_h = text_h + pill_padding_y * 2 + 10
    
    draw.rounded_rectangle(
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=pill_h//2, fill=pill_color
    )
    # text inside pill
    draw.text((pill_x + pill_padding_x, pill_y + pill_padding_y), category, font=font_pill, fill=(255, 255, 255))
    
    # 3. Draw Center Text
    # Title
    t_bbox = draw.textbbox((0, 0), title, font=font_title)
    t_w = t_bbox[2] - t_bbox[0]
    draw.text(((W - t_w) // 2, 220), title, font=font_title, fill=(255, 255, 255))
    
    # Subtitle
    s_bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    s_w = s_bbox[2] - s_bbox[0]
    draw.text(((W - s_w) // 2, 340), subtitle, font=font_sub, fill=(255, 255, 255))
    
    # Paper Count
    if paper_count:
        p_text = f"論文数：{paper_count}"
        p_bbox = draw.textbbox((0, 0), p_text, font=font_paper)
        p_w = p_bbox[2] - p_bbox[0]
        # Align to the right of the center block
        draw.text(((W + s_w) // 2 - p_w, 440), p_text, font=font_paper, fill=(160, 170, 180))

    bg.save(output_path)
    print(f"Saved: {output_path}")

def main():
    base_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
    out_dir = os.path.join(base_dir, 'Note_Thumbnails')
    os.makedirs(out_dir, exist_ok=True)
    
    count = 0
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path) or '_' not in folder:
            continue
            
        parts = folder.split('_')
        if len(parts) >= 4:
            day = parts[0]
            category = parts[1]
            title = parts[2]
            subtitle = '_'.join(parts[3:])
            
            # extract paper count
            paper_count = "9" # default roughly
            ig_csv = os.path.join(folder_path, 'ig_carousel_data.csv')
            sns_md = os.path.join(folder_path, 'sns_all_drafts.md')
            
            p_found = False
            if os.path.exists(ig_csv):
                with open(ig_csv, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    m = re.search(r'論文(?:数)?\s*[:：]\s*(\d+)', content)
                    if m:
                        paper_count = m.group(1)
                        p_found = True
            
            if not p_found and os.path.exists(sns_md):
                with open(sns_md, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    m = re.search(r'論文(?:数)?\s*[:：]\s*(\d+)', content)
                    if not m:
                        m = re.search(r'(\d+)\s*報', content)
                    if m:
                        paper_count = m.group(1)
            
            out_name = f"{folder}_thumbnail.png"
            out_path = os.path.join(out_dir, out_name)
            
            generate_thumbnail(day, category, title, subtitle, paper_count, out_path)
            count += 1
            if count == 1:
                print(f"Generated sample: {out_path}")
                # We can break here for test, or continue for all. Let's do all.
    print(f"Total generated: {count}")

if __name__ == '__main__':
    main()
