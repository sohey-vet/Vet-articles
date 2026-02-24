import os
from bs4 import BeautifulSoup
from pathlib import Path

base_dir = Path(r'c:\Users\souhe\Desktop\論文まとめ\topics\救急')
dka_file = base_dir / '猫の糖尿病性ケトアシドーシス_DKAの緊急管理.html'
hhs_file = base_dir / '犬の高浸透圧高血糖症候群_HHSの罠.html'
ate_file = base_dir / '猫の動脈血栓塞栓症_ATEの初期対応と予後.html'

def insert_section_before_footer(soup, html_snippet):
    footer = soup.find('footer', class_='page-footer')
    if footer:
        snippet_soup = BeautifulSoup(html_snippet, 'html.parser')
        footer.insert_before(snippet_soup)

# --- DKA Refs ---
dka_refs = """
<div id="refs">
    <div class="accordion">
        <button class="accordion-trigger">
            <span class="trigger-left"><span class="trigger-icon">📚</span><span>参照論文（3本）</span></span>
            <span class="chevron">▼</span>
        </button>
        <div class="accordion-content">
            <div class="accordion-body">
                <ol style="padding-left:20px;font-size:0.82rem;color:var(--color-text-secondary);">
                    <li>Behrend E et al. 2018 AAHA Diabetes Management Guidelines for Dogs and Cats. <em>J Am Anim Hosp Assoc</em> 2018;54(1):1-21.</li>
                    <li>Silverstein DC, Hopper K. <em>Small Animal Critical Care Medicine, 3rd ed.</em> Elsevier, 2023.</li>
                    <li>DiTommaso M et al. Evaluation of a continuous regular insulin infusion protocol for the treatment of feline diabetic ketoacidosis. <em>J Feline Med Surg</em> 2020.</li>
                </ol>
            </div>
        </div>
    </div>
</div>
"""

# --- HHS Refs ---
hhs_refs = """
<div id="refs">
    <div class="accordion">
        <button class="accordion-trigger">
            <span class="trigger-left"><span class="trigger-icon">📚</span><span>参照論文（3本）</span></span>
            <span class="chevron">▼</span>
        </button>
        <div class="accordion-content">
            <div class="accordion-body">
                <ol style="padding-left:20px;font-size:0.82rem;color:var(--color-text-secondary);">
                    <li>Schermerhorn T. Hyperosmolar hyperglycemic syndrome. <em>Vet Clin North Am Small Anim Pract</em> 2013;43(2):331-344.</li>
                    <li>Silverstein DC, Hopper K. <em>Small Animal Critical Care Medicine, 3rd ed.</em> Elsevier, 2023.</li>
                    <li>Behrend E et al. 2018 AAHA Diabetes Management Guidelines for Dogs and Cats. <em>J Am Anim Hosp Assoc</em> 2018;54(1):1-21.</li>
                </ol>
            </div>
        </div>
    </div>
</div>
"""

# --- ATE Owner Tips & Refs ---
ate_owner_tips = """
<div id="owner-tips">
    <div class="accordion">
        <button class="accordion-trigger">
            <span class="trigger-left"><span class="trigger-icon">🗣️</span><span>飼い主への説明ガイド</span></span>
            <span class="chevron">▼</span>
        </button>
        <div class="accordion-content">
            <div class="accordion-body premium-content">
                <div class="owner-tip" style="margin-top:0;">
                    <h4>治る見込みはありますか？</h4>
                    <div class="speech-bubble">
                        発見が早く、片脚のみの軽度な麻痺であれば歩けるようになる可能性もありますが、両脚が完全に麻痺して体温が低い場合は非常に危険な状態（生存率30%以下）です。また心臓の重い病気が原因であるため、血栓が溶けても急な心不全や心停止のリスクが常に伴います。
                    </div>
                </div>
                <div class="owner-tip">
                    <h4>すぐに手術で血栓を取れませんか？</h4>
                    <div class="speech-bubble">
                        猫の場合、血管が非常に細く、全身状態が極めて悪いため手術（血栓摘出術）は通常推奨されません。お薬で血栓の広がりを抑えながら、強い痛みを取り除き、心臓を休ませる治療が中心となります。
                    </div>
                </div>
            </div>
            <div class="premium-lock"><span class="lock-icon">🔒</span>飼い主説明ガイドは有料会員限定です</div>
        </div>
    </div>
</div>
"""

ate_refs = """
<div id="refs">
    <div class="accordion">
        <button class="accordion-trigger">
            <span class="trigger-left"><span class="trigger-icon">📚</span><span>参照論文（3本）</span></span>
            <span class="chevron">▼</span>
        </button>
        <div class="accordion-content">
            <div class="accordion-body">
                <ol style="padding-left:20px;font-size:0.82rem;color:var(--color-text-secondary);">
                    <li>Borgeat K et al. Arterial thromboembolism in 250 cats in general practice: 2004-2012. <em>J Vet Intern Med</em> 2014;28(1):102-108.</li>
                    <li>Smith SA et al. Arterial thromboembolism in cats: acute crisis in 127 cases (1992-2001) and long-term management with low-dose aspirin in 24 cases. <em>J Vet Intern Med</em> 2003;17(1):73-83.</li>
                    <li>Hogan DF et al. Secondary prevention of cardiogenic arterial thromboembolism in the cat: The FAT CAT trial. <em>J Vet Cardiol</em> 2015;17 Suppl 1:S306-S314.</li>
                </ol>
            </div>
        </div>
    </div>
</div>
"""

def update_file(path, snippets):
    with open(path, 'r', encoding='utf-8') as fh:
        soup = BeautifulSoup(fh, 'html.parser')
    changed = False
    for snippet in snippets:
        # Avoid duplicate insertion
        if 'owner-tips' in snippet and not soup.find(id='owner-tips'):
            insert_section_before_footer(soup, snippet)
            changed = True
        elif 'refs' in snippet and not soup.find(id='refs'):
            insert_section_before_footer(soup, snippet)
            changed = True
            
    if changed:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(str(soup))
        print(f"Updated {path.name}")

if __name__ == '__main__':
    if dka_file.exists(): update_file(dka_file, [dka_refs])
    if hhs_file.exists(): update_file(hhs_file, [hhs_refs])
    if ate_file.exists(): update_file(ate_file, [ate_owner_tips, ate_refs])
    print("Repair script complete.")
