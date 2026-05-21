import subprocess
import time

dates = [
    "2026-06-03",
    "2026-06-05"
]

print("Starting batch Note draft generation for next 2 articles...")

for d in dates:
    print(f"\n[{d}] Processing Note draft...")
    result = subprocess.run(["python", "auto_post_note.py", "--date", d, "--draft"])
    
    if result.returncode != 0:
        print(f"Error occurred during processing for {d}. Stopping batch process.")
        break
    
    print(f"Successfully processed {d}. Waiting 5 seconds before next...")
    time.sleep(5)

print("\nBatch processing complete!")
