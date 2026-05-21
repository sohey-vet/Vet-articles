import subprocess
import time

dates = [
    "2026-05-15",
    "2026-05-18",
    "2026-05-20",
    "2026-05-22",
    "2026-05-25",
    "2026-05-27",
    "2026-05-29",
    "2026-06-01"
]

print("Starting batch Note draft generation for 8 articles...")

for d in dates:
    print(f"\n[{d}] Processing Note draft...")
    result = subprocess.run(["python", "auto_post_note.py", "--date", d, "--draft"])
    
    if result.returncode != 0:
        print(f"Error occurred during processing for {d}. Stopping batch process.")
        break
    
    print(f"Successfully processed {d}. Waiting 5 seconds before next...")
    time.sleep(5)

print("\nBatch processing complete!")
