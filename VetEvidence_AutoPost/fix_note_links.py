import os

root_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename == 'sns_all_drafts.md':
            fpath = os.path.join(dirpath, filename)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '🔗note.com' in content:
                new_content = content.replace('🔗note.com', '🔗 https://note.com')
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                print(f"Fixed {fpath}")

print(f'Fixed {count} drafts.')

# Fix rewrite_long_threads_volume.py if needed
py_fpath = os.path.join(root_dir, 'VetEvidence_AutoPost', 'rewrite_long_threads_volume.py')
if os.path.exists(py_fpath):
    with open(py_fpath, 'r', encoding='utf-8') as f:
        py_content = f.read()
    if '🔗note.com' in py_content:
        py_new = py_content.replace('🔗note.com', '🔗 https://note.com')
        with open(py_fpath, 'w', encoding='utf-8') as f:
            f.write(py_new)
        print("Fixed rewrite_long_threads_volume.py")
