import os

root_dir = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts'
count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename == 'sns_all_drafts.md':
            fpath = os.path.join(dirpath, filename)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'note.com/pawmedical_jp' in content:
                    # replace all occurrences but avoid double https
                    new_content = content.replace('note.com/pawmedical_jp', 'https://note.com/pawmedical_jp')
                    new_content = new_content.replace('https://https://', 'https://')
                    
                    if new_content != content:
                        with open(fpath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        count += 1
            except Exception as e:
                pass

print('Fixed', count, 'draft files.')

# Also fix the rewrite script just in case
py_fpath = os.path.join(root_dir, 'VetEvidence_AutoPost', 'rewrite_long_threads_volume.py')
if os.path.exists(py_fpath):
    with open(py_fpath, 'r', encoding='utf-8') as f:
        py_content = f.read()
    py_new = py_content.replace('note.com/pawmedical_jp', 'https://note.com/pawmedical_jp').replace('https://https://', 'https://')
    if py_new != py_content:
        with open(py_fpath, 'w', encoding='utf-8') as f:
            f.write(py_new)
        print('Fixed rewrite_long_threads_volume.py')

