/* ═══════════════════════════════════════════════════════════
   WANDERLY — main.js (Redesigned)
   Vanilla JS. Parallax floats · text rotate · tabs · chat
═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── 1. ALERTS ─────────────────────────────────────────── */
  document.querySelectorAll('.alert').forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) closeBtn.addEventListener('click', () => dismiss(alert));
    setTimeout(() => dismiss(alert), 5000);
  });
  function dismiss(el) {
    el.style.transition = 'opacity .3s ease, transform .3s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-6px)';
    setTimeout(() => el.remove(), 350);
  }

  /* ── 2. PARALLAX FLOATING IMAGES ───────────────────────── */
  const floats = document.querySelectorAll('.float-img, .auth-float-img');
  if (floats.length) {
    const depths = [0.018, 0.032, 0.024, 0.028, 0.020, 0.014, 0.026];
    let mx = 0, my = 0, cx = 0, cy = 0;

    window.addEventListener('mousemove', e => {
      const w = window.innerWidth, h = window.innerHeight;
      mx = (e.clientX - w / 2);
      my = (e.clientY - h / 2);
    }, { passive: true });

    (function animateFloats() {
      cx += (mx - cx) * 0.06;
      cy += (my - cy) * 0.06;
      floats.forEach((el, i) => {
        const d = depths[i % depths.length];
        const tx = cx * d, ty = cy * d;
        const r = parseFloat(getComputedStyle(el).getPropertyValue('--r') || '0');
        el.style.transform = `translate(${tx}px, ${ty}px) rotate(${r}deg)`;
      });
      requestAnimationFrame(animateFloats);
    })();
  }

  /* ── 3. TEXT ROTATE ─────────────────────────────────────── */
  // Handled via CSS animation on .rotate-inner — no JS needed
  // But we add a JS fallback for browsers that need it
  const rotateInner = document.querySelector('.rotate-inner');
  if (rotateInner) {
    const words = Array.from(rotateInner.querySelectorAll('.rotate-word'));
    const count = words.length;
    if (count && !CSS.supports('animation', 'textSlide 1s')) {
      let i = 0;
      words.forEach((w, idx) => { w.style.display = idx === 0 ? 'block' : 'none'; });
      setInterval(() => {
        words[i].style.display = 'none';
        i = (i + 1) % count;
        words[i].style.display = 'block';
      }, 2400);
    }
  }

  /* ── 4. HERO SEARCH ─────────────────────────────────────── */
  const heroSearch = document.getElementById('hero-search');
  const citiesGrid = document.getElementById('cities-grid');
  if (heroSearch && citiesGrid) {
    heroSearch.addEventListener('input', function () {
      const q = this.value.toLowerCase().trim();
      citiesGrid.querySelectorAll('.city-card').forEach(card => {
        card.style.display = (card.dataset.name || '').includes(q) ? '' : 'none';
      });
    });
    // Also handle the inline search bar in hero
    const heroSearchBtn = document.getElementById('hero-search-btn');
    if (heroSearchBtn) {
      heroSearchBtn.addEventListener('click', () => {
        const section = document.getElementById('cities-section');
        if (section) section.scrollIntoView({ behavior: 'smooth' });
      });
    }
  }

  /* ── 5. TAB SYSTEM ──────────────────────────────────────── */
  document.querySelectorAll('[data-tabs]').forEach(tabGroup => {
    const buttons = tabGroup.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Find panels — search within tabGroup's parent or document
        const container = tabGroup.closest('.container') || document;
        container.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        const panel = container.querySelector(`[data-panel="${target}"]`);
        if (panel) panel.classList.add('active');
      });
    });
  });

  /* ── 6. SCROLL REVEAL ───────────────────────────────────── */
  const ro = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        ro.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

  document.querySelectorAll('.reveal').forEach((el, i) => {
    el.style.transitionDelay = `${i * 55}ms`;
    ro.observe(el);
  });

  /* ── 7. CHAT ────────────────────────────────────────────── */
  const chatMessages = document.querySelector('.chat-messages');
  if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;

  const chatTextarea = document.querySelector('.chat-input-area textarea');
  if (chatTextarea) {
    chatTextarea.addEventListener('input', () => {
      chatTextarea.style.height = 'auto';
      chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 120) + 'px';
    });
    chatTextarea.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        chatTextarea.closest('form').submit();
      }
    });
  }

  /* ── 8. STAR RATING ─────────────────────────────────────── */
  document.querySelectorAll('.star-picker').forEach(picker => {
    const labels = [...picker.querySelectorAll('label')].reverse();
    const inputs = picker.querySelectorAll('input');
    inputs.forEach(input => {
      input.addEventListener('change', () => {
        labels.forEach((l, i) => {
          l.style.color = i < +input.value ? 'var(--gold)' : '';
        });
      });
    });
  });

  /* ── 9. CONFIRM DIALOGS ─────────────────────────────────── */
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => {
      if (!confirm(btn.dataset.confirm)) e.preventDefault();
    });
  });

  /* ── 10. LIGHTBOX ───────────────────────────────────────── */
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightbox-img');
  if (lb && lbImg) {
    document.querySelectorAll('.gallery-item[data-src]').forEach(item => {
      item.addEventListener('click', () => {
        lbImg.src = item.dataset.src;
        lb.classList.add('open');
      });
    });
    lb.addEventListener('click', e => {
      if (e.target === lb || e.target.closest('.lightbox-close')) lb.classList.remove('open');
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') lb.classList.remove('open');
    });
  }

  /* ── 11. IMAGE CAROUSEL ─────────────────────────────────── */
  const carousel = document.getElementById('carousel');
  if (carousel) {
    let idx = 0;
    const slides = carousel.querySelectorAll('.carousel-slide');
    const total = slides.length;
    window.carouselNext = () => { idx = (idx + 1) % total; carousel.style.transform = `translateX(-${idx * 100}%)`; };
    window.carouselPrev = () => { idx = (idx - 1 + total) % total; carousel.style.transform = `translateX(-${idx * 100}%)`; };
  }

  /* ── 12. LIKE FORM AJAX ─────────────────────────────────── */
  document.querySelectorAll('.like-form').forEach(form => {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const btn = form.querySelector('.like-btn');
      if (!btn) return;
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value },
        });
        if (res.ok) {
          btn.classList.toggle('liked');
          const svg = btn.querySelector('svg');
          if (svg) svg.setAttribute('fill', btn.classList.contains('liked') ? 'currentColor' : 'none');
        }
      } catch { form.submit(); }
    });
  });

  /* ── 13. MOBILE NAV HIDE ON SCROLL ─────────────────────── */
  let lastY = 0;
  const nav = document.querySelector('.nav');
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (nav && y > 100) {
      nav.style.transform = y > lastY ? 'translateY(-100%)' : 'translateY(0)';
    }
    lastY = y;
  }, { passive: true });

});
