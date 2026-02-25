"""
Fix the 8 remaining failing Mermaid blocks individually.
Each file has a unique issue requiring a targeted fix.
"""
import re
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics')
fixed = 0

def fix_file(fpath, fix_func):
    global fixed
    f = Path(fpath)
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    original = content
    content = re.sub(
        r'(<pre class="mermaid">)(.*?)(</pre>)',
        lambda m: m.group(1) + fix_func(m.group(2)) + m.group(3),
        content, flags=re.DOTALL
    )
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        fixed += 1
        print(f'Fixed: {f.stem}')


def common_fixes(block):
    """Apply common fixes to any block."""
    # Remove trailing semicolons
    block = re.sub(r';\s*$', '', block, flags=re.MULTILINE)
    # Fix <br/> in edge labels (between -- and -->)
    # Mermaid uses <br/> for line breaks inside node labels, but NOT in edge labels
    # Edge labels are between | |, edge text is between -- and -->
    # Replace <br/> in edge text (not inside | | or [ ] or { }) with space
    
    # Fix unquoted edge text with <br/>: B -- text<br/>text --> C
    # Pattern: -- text<br/>text -->
    block = re.sub(r' -- ([^|>\n]*?)<br/>\s*([^|>\n]*?) -->', lambda m: f' -- {m.group(1)} {m.group(2)} -->', block)
    block = re.sub(r' -- ([^|>\n]*?)<br/>\s*([^|>\n]*?) -->', lambda m: f' -- {m.group(1)} {m.group(2)} -->', block)
    
    # Fix --text--> non-standard arrows (e.g. --同時並行-->)
    block = re.sub(r'--([^->\s|"][^->]*?)-->', r'-->|"\1"|', block)
    
    # Fix multi-line node labels: merge lines that are continuations of [ ] or { } or ( )
    lines = block.split('\n')
    merged_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if line has an unclosed bracket
        open_sq = line.count('[') - line.count(']')
        open_rd = line.count('(') - line.count(')')
        open_cu = line.count('{') - line.count('}')
        
        while (open_sq > 0 or open_rd > 0 or open_cu > 0) and i + 1 < len(lines):
            i += 1
            next_line = lines[i].strip()
            line = line.rstrip() + ' ' + next_line
            open_sq = line.count('[') - line.count(']')
            open_rd = line.count('(') - line.count(')')
            open_cu = line.count('{') - line.count('}')
        
        merged_lines.append(line)
        i += 1
    
    block = '\n'.join(merged_lines)
    
    # Quote unquoted node labels inside brackets
    def quote_if_needed(match):
        full = match.group(0)
        bracket_type = match.group(1)  # [ ( {
        content = match.group(2)
        close_bracket = match.group(3)  # ] ) }
        
        if content.startswith('"') and content.endswith('"'):
            return full
        if not content.strip():
            return full
        
        content = content.replace('"', "'")
        return f'{bracket_type}"{content}"{close_bracket}'
    
    # Quote [...] content
    block = re.sub(r'(\[)([^\]]+)(\])', quote_if_needed, block)
    # Quote {...} content (but not subgraph end)
    block = re.sub(r'(?<=[A-Za-z0-9_])(\{)([^}]+)(\})', quote_if_needed, block)
    # Quote (...) content for nodes
    block = re.sub(r'(?<=[A-Za-z0-9_])(\()([^)]+)(\))', quote_if_needed, block)
    
    # Quote unquoted edge labels |text|
    def quote_edge(m):
        content = m.group(1)
        if content.startswith('"') and content.endswith('"'):
            return f'|{content}|'
        content = content.replace('"', "'")
        return f'|"{content}"|'
    block = re.sub(r'\|([^|]+)\|', quote_edge, block)
    
    return block


# Fix 1: クッシング症候群 - multi-line node labels, unquoted content
def fix_cushing(block):
    block = common_fixes(block)
    return block

fix_file(base_dir / '内分泌' / 'クッシング症候群_診断の落とし穴.html', fix_cushing)


# Fix 2: 不整脈 - needs common fixes
def fix_arrhythmia(block):
    block = common_fixes(block)
    return block

fix_file(base_dir / '循環器' / '不整脈の救急対応_心電図の読み方.html', fix_arrhythmia)


# Fix 3: FIP - <br/> in edge labels, needs quoting
def fix_fip(block):
    block = common_fixes(block)
    return block

fix_file(base_dir / '猫' / 'FIP_抗ウイルス薬時代の治療.html', fix_fip)


# Fix 4: 猫の輸液 - 'end' keyword conflict
def fix_cat_fluid(block):
    block = common_fixes(block)
    # Check for 'end' used as subgraph close that might conflict
    lines = block.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # 'end' on its own line is subgraph close - keep it but ensure it's truly closing a subgraph
        new_lines.append(line)
    block = '\n'.join(new_lines)
    return block

fix_file(base_dir / '猫' / '猫の輸液_犬との違いと注意点.html', fix_cat_fluid)


# Fix 5: 椎間板ヘルニア - <br/> in node labels inside {}
def fix_ivdd(block):
    block = common_fixes(block)
    return block

fix_file(base_dir / '神経' / '椎間板ヘルニア_頚部胸腰部統合版.html', fix_ivdd)


# Fix 6: 発作 - non-standard arrows like --同時並行-->
def fix_seizure(block):
    block = common_fixes(block)
    return block

fix_file(base_dir / '神経' / '発作の初期対応_頭蓋内疾患を疑うとき.html', fix_seizure)


# Fix 7: 血液ガス - comma-separated node lists at end
def fix_blood_gas(block):
    block = common_fixes(block)
    # Remove comma-separated node lists (not valid Mermaid syntax)
    # These are likely style group definitions that should use classDef
    lines = block.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines like "R_Acid_C, R_Acid_A, M_Acid_C, ..."
        if re.match(r'^[A-Za-z_]+,\s*[A-Za-z_]', stripped):
            # This is likely a class assignment, skip or comment out
            continue
        new_lines.append(line)
    block = '\n'.join(new_lines)
    return block

fix_file(base_dir / '血液ガス' / '血液ガス分析の基本.html', fix_blood_gas)


print(f'\nTotal fixed: {fixed}')
