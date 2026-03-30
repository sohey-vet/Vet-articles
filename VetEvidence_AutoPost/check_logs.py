import os

log_file = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\logs\x_schedule_1week_log_20260329.log"
output_file = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\temp_out.txt"

if not os.path.exists(log_file):
    print("Log file not found")
else:
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_target = "Unknown Target"
    results = []
    
    for line in lines:
        line = line.strip()
        if "📝 対象:" in line:
            current_target = line.split("📝 対象:")[-1].strip()
            
        if "WARNING" in line or "ERROR" in line or "失敗" in line or "文字数" in line:
            results.append(f"【{current_target}】 {line}")
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(results) if results else "No issues found.")
