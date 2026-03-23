import subprocess
import os

repo_dir = r"C:\Users\souhe\Desktop\論文まとめ"

def run_git(args):
    result = subprocess.run(["git", "-C", repo_dir] + args, capture_output=True, text=True, encoding='utf-8')
    return result.stdout.strip()

# The bad commit where things got deleted is the one with message "Fix md_to_site_html.py..."
# Let's find its hash
log_lines = run_git(["log", "--oneline", "-n", "10"]).split('\n')
bad_commit = None
good_commit = None

for i, line in enumerate(log_lines):
    if "Fix md_to_site_html.py" in line:
        bad_commit = line.split()[0]
        if i + 1 < len(log_lines):
            good_commit = log_lines[i + 1].split()[0]
        break

if not good_commit:
    print("Could not find the target commits.")
    exit(1)

print(f"Good commit was: {good_commit}")
print(f"Bad commit was: {bad_commit}")

diff_out = run_git(["diff", "--name-status", "--diff-filter=D", good_commit, bad_commit])
lines = diff_out.split('\n')
deleted_html_files = []

for line in lines:
    line = line.strip()
    if not line: continue
    parts = line.split('\t')
    if len(parts) >= 2:
        status, filepath = parts[0], parts[1]
        
        # Unescape git's output if it has octal quotes
        if filepath.startswith('"') and filepath.endswith('"'):
            # Convert octal sequences to proper unicode is annoying, but Python's eval or unicode_escape can do it
            try:
                # `\346\225` etc is UTF-8 octal bytes
                b = eval(f"b{filepath}")
                filepath = b.decode('utf-8')
            except:
                pass
                
        if filepath.startswith("topics/") and filepath.endswith(".html"):
            deleted_html_files.append(filepath)

print(f"Found {len(deleted_html_files)} deleted HTML files in topics/.")

# Now compare against current existing ones, and if missing, checkout from good_commit
restored = 0
for filepath in deleted_html_files:
    full_path = os.path.join(repo_dir, filepath)
    if not os.path.exists(full_path):
        # Restore it!
        run_git(["checkout", good_commit, "--", filepath])
        restored += 1
        print(f"Restored: {filepath}")

print(f"Total restored files: {restored}")
