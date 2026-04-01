import os
import glob
import re

base_dir = r'c:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
files = glob.glob(os.path.join(base_dir, '**', 'sns_all_drafts.md'), recursive=True)

output_file = os.path.join(base_dir, 'tmp_threads_drafts.md')

with open(output_file, 'w', encoding='utf-8') as outfile:
    count = 0
    for f in files:
        with open(f, 'r', encoding='utf-8') as infile:
            content = infile.read()
        
        # Regex to find Threads block
        match = re.search(r'## 🧵 Threads用[^\n]*\n(.*?)---', content, re.DOTALL)
        if match:
            threads_content = match.group(1).strip()
            # Extract just the markdown code block text
            code_match = re.search(r'```text\n(.*?)```', threads_content, re.DOTALL)
            if code_match:
                threads_content = code_match.group(1).strip()
            
            folder_name = os.path.basename(os.path.dirname(f))
            outfile.write(f'### {folder_name}\n')
            outfile.write(f'{threads_content}\n\n')
            count += 1

print(f'Extracted {count} files into {output_file}')
