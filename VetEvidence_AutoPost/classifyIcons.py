import os
import glob
import time
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('gemini-1.5-flash')

folder_path = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\minimal_icons"
categories = [
    "01_emergency", "02_cardiology", "03_fluids", "04_nephrology",
    "05_cat", "06_dermatology", "07_immunology", "08_blood",
    "09_gi_liver", "10_oncology", "11_neurology", "12_endocrinology",
    "13_anesthesia", "14_ophthalmology", "15_dentistry", "16_other"
]

prompt = f"""
You are a highly accurate medical icon classifier.
Analyze the provided image and classify it into exactly one of the following 16 categories based on the visual motif:
{', '.join(categories)}

Guideline:
01_emergency = ambulance, red cross, siren
02_cardiology = heart, ecg line
03_fluids = IV bag, drip
04_nephrology = kidney
05_cat = cat silhouette
06_dermatology = skin, fingerprint, hair
07_immunology = shield, lock
08_blood = blood drop
09_gi_liver = stomach, liver, intestines
10_oncology = microscope, cancer cell
11_neurology = brain, neuron
12_endocrinology = scale, balance, thyroid
13_anesthesia = anesthesia monitor, breathing bag, mask
14_ophthalmology = eye, eyeball
15_dentistry = tooth, teeth
16_other = generic med kit, cross, handle box, anything not fitting above

Output ONLY the exact category name from the list. No markdown formatting, no punctuation, no explanations.
"""

def main():
    print("Starting AI Image Classification for minimal_icons...")
    image_files = glob.glob(os.path.join(folder_path, "*.*"))
    processed_count = 0
    
    for img_path in image_files:
        ext = os.path.splitext(img_path)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            continue
            
        filename = os.path.basename(img_path)
        
        # Skip if already perfectly matches a category
        if any(filename.startswith(cat) for cat in categories):
            continue

        print(f"Analyzing {filename} with Gemini 1.5 Flash...")
        try:
            img = Image.open(img_path)
            response = model.generate_content([prompt, img])
            category = response.text.strip().replace("'", "").replace('"', '').replace('`', '')
            
            if category in categories:
                new_filename = f"{category}{ext}"
                new_path = os.path.join(folder_path, new_filename)
                
                # Deduplication
                counter = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(folder_path, f"{category}_{counter}{ext}")
                    counter += 1
                    
                os.rename(img_path, new_path)
                print(f"✅ Renamed: {filename} -> {os.path.basename(new_path)}")
                processed_count += 1
            else:
                print(f"❌ Failed to classify {filename} (Model outputted: {category})")
                new_path = os.path.join(folder_path, f"16_other_{int(time.time())}{ext}")
                os.rename(img_path, new_path)
                print(f"⚠️ Fallback Renamed: {filename} -> {os.path.basename(new_path)}")
                processed_count += 1
                
            time.sleep(2)
        except Exception as e:
            print(f"🚨 Error processing {filename}: {e}")

    print(f"Done! Processed {processed_count} images.")

if __name__ == "__main__":
    main()
