/**
 * 獣医論文まとめ - Interactive Scripts v2
 */

document.addEventListener('DOMContentLoaded', () => {
  initBreadcrumb();
  initAccordions();
  initFadeAnimations();
  initMobileNav();
  initContentModeToggle();
  initBackToTop();
  initCollapsibleFlowcharts();
});

/**
 * Accordion
 */
function initAccordions() {
  const accordions = document.querySelectorAll('.accordion');

  // 初期状態ですべてのアコーディオンを開く
  accordions.forEach(accordion => {
    accordion.classList.add('open');
    const content = accordion.querySelector('.accordion-content');
    content.style.maxHeight = 'none'; // 最初から全開
  });

  const triggers = document.querySelectorAll('.accordion-trigger');
  triggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const accordion = trigger.closest('.accordion');
      const content = accordion.querySelector('.accordion-content');
      const isOpen = accordion.classList.contains('open');

      if (isOpen) {
        content.style.maxHeight = content.scrollHeight + 'px';
        requestAnimationFrame(() => { content.style.maxHeight = '0'; });
        accordion.classList.remove('open');
      } else {
        accordion.classList.add('open');
        content.style.maxHeight = content.scrollHeight + 'px';
        content.addEventListener('transitionend', function handler() {
          if (accordion.classList.contains('open')) {
            content.style.maxHeight = 'none';
          }
          content.removeEventListener('transitionend', handler);
        });
      }
    });
  });
}

/**
 * Fade animations
 */
function initFadeAnimations() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in-up');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.card, .accordion, .key-findings, .clinical-tip, .bottom-line, .owner-tip').forEach(el => {
    // free-content内の要素はアニメーション対象外（即表示）
    if (el.closest('.free-content')) return;
    el.style.opacity = '0';
    observer.observe(el);
  });
}

/**
 * Toggle all accordions
 */
function toggleAllAccordions(open) {
  const accordions = document.querySelectorAll('.accordion');
  accordions.forEach(accordion => {
    const content = accordion.querySelector('.accordion-content');
    if (open && !accordion.classList.contains('open')) {
      accordion.classList.add('open');
      content.style.maxHeight = 'none';
    } else if (!open && accordion.classList.contains('open')) {
      content.style.maxHeight = content.scrollHeight + 'px';
      requestAnimationFrame(() => { content.style.maxHeight = '0'; });
      accordion.classList.remove('open');
    }
  });
}

/**
 * Mobile Navigation (Hamburger Menu)
 */
function initMobileNav() {
  const hamburger = document.querySelector('.hamburger-btn');
  const slideMenu = document.querySelector('.slide-menu');
  const overlay = document.querySelector('.slide-menu-overlay');

  if (!hamburger || !slideMenu) return;

  function toggleMenu() {
    hamburger.classList.toggle('open');
    slideMenu.classList.toggle('open');
    if (overlay) overlay.classList.toggle('open');
    document.body.style.overflow = slideMenu.classList.contains('open') ? 'hidden' : '';
  }

  hamburger.addEventListener('click', toggleMenu);
  if (overlay) overlay.addEventListener('click', toggleMenu);

  // Close menu on link click
  slideMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if (slideMenu.classList.contains('open')) toggleMenu();
    });
  });
}

/**
 * Content Mode Toggle (Free / Premium)
 * Noteでの有料化を見据えた切り替え機能
 */
function initContentModeToggle() {
  const toggle = document.getElementById('content-mode-toggle');
  if (!toggle) return;

  // Default to premium mode
  const saved = localStorage.getItem('vetevidence-mode');
  if (saved === 'free') {
    document.body.classList.add('mode-free');
    document.body.classList.remove('mode-premium');
    toggle.checked = false;
  } else {
    document.body.classList.add('mode-premium');
    document.body.classList.remove('mode-free');
    toggle.checked = true;
  }

  toggle.addEventListener('change', () => {
    if (toggle.checked) {
      document.body.classList.remove('mode-free');
      document.body.classList.add('mode-premium');
      localStorage.setItem('vetevidence-mode', 'premium');
    } else {
      document.body.classList.add('mode-free');
      document.body.classList.remove('mode-premium');
      localStorage.setItem('vetevidence-mode', 'free');
    }
  });

  // Update label text
  updateModeLabel(toggle.checked);
  toggle.addEventListener('change', () => updateModeLabel(toggle.checked));
}

function updateModeLabel(isPremium) {
  const label = document.querySelector('.mode-label');
  if (label) {
    label.textContent = isPremium ? '👑 すべて表示' : '🔒 概要のみ';
  }
}

/**
 * Back to Top Button
 */
function initBackToTop() {
  const btn = document.createElement('button');
  btn.className = 'back-to-top';
  btn.setAttribute('aria-label', 'トップに戻る');
  btn.innerHTML = '↑';
  document.body.appendChild(btn);

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/**
 * Breadcrumb Navigation - Back to Index
 * 個別記事ページにトップへ戻るナビを動的挿入（index.htmlでは非表示）
 */
function initBreadcrumb() {
  // index.htmlでは挿入しない
  const path = window.location.pathname;
  if (path.endsWith('index.html') || path.endsWith('/')) return;

  const container = document.querySelector('.page-container');
  if (!container) return;

  // 既に存在する場合はスキップ
  if (container.querySelector('.breadcrumb-nav')) return;

  const nav = document.createElement('nav');
  nav.className = 'breadcrumb-nav';
  nav.innerHTML = '<a href="../../index.html"><span class="back-arrow">←</span> トップに戻る</a>';
  container.insertBefore(nav, container.firstChild);
}

/**
 * Collapsible Flowcharts
 * Mermaid diagrams are collapsed by default. Users click to expand.
 * Uses a short delay to let Mermaid render SVGs first.
 */
function initCollapsibleFlowcharts() {
  // Wait for Mermaid to finish rendering
  setTimeout(() => {
    const wrappers = document.querySelectorAll('.mermaid-wrapper');
    wrappers.forEach(wrapper => {
      // Skip if already wrapped
      if (wrapper.parentElement.tagName === 'DETAILS') return;

      const details = document.createElement('details');
      details.className = 'flowchart-collapse';

      const summary = document.createElement('summary');
      summary.className = 'flowchart-toggle';
      summary.innerHTML = '📊 フローチャートを表示';

      // Insert details before wrapper, then move wrapper inside
      wrapper.parentNode.insertBefore(details, wrapper);
      details.appendChild(summary);
      details.appendChild(wrapper);

      // Update text on toggle
      details.addEventListener('toggle', () => {
        summary.innerHTML = details.open
          ? '📊 フローチャートを閉じる'
          : '📊 フローチャートを表示';
      });
    });
  }, 2500);
}

