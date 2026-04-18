/* ================================================================
   Wanderly — main.js
   Theme · Nav · Scroll animations · Parallax · Count-up · Chat
   ================================================================ */

/* ── Theme init (before DOMContentLoaded) ────────────────────── */
!function () {
  var s = localStorage.getItem('wanderly-theme');
  var d = window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.setAttribute('data-theme', s || (d ? 'dark' : 'light'));
}();

document.addEventListener('DOMContentLoaded', () => {

  /* ── Scroll progress bar ─────────────────────────────────── */
  const bar = document.createElement('div');
  bar.id = 'scroll-progress';
  document.body.prepend(bar);
  window.addEventListener('scroll', () => {
    const pct = window.scrollY / (document.body.scrollHeight - window.innerHeight) * 100;
    bar.style.width = Math.min(pct, 100) + '%';
  }, { passive: true });

  /* ── Nav hide/show + scrolled shadow ────────────────────── */
  const nav = document.getElementById('main-nav');
  let lastY = 0;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (nav) {
      nav.classList.toggle('scrolled', y > 10);
      if (y > 120) nav.style.transform = y > lastY ? 'translateY(-100%)' : 'translateY(0)';
      else nav.style.transform = 'translateY(0)';
    }
    lastY = y;
  }, { passive: true });

  /* ── Theme toggle ────────────────────────────────────────── */
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('wanderly-theme', next);
    });
  });

  /* ── Auto-dismiss Django messages / alerts ───────────────── */
  document.querySelectorAll('.alert').forEach(el => {
    const close = el.querySelector('.alert-close');
    const dismiss = () => {
      el.style.transition = 'opacity .3s ease, transform .3s ease';
      el.style.opacity = '0'; el.style.transform = 'translateY(-6px)';
      setTimeout(() => el.remove(), 350);
    };
    if (close) close.addEventListener('click', dismiss);
    setTimeout(dismiss, 5000);
  });

  /* ══════════════════════════════════════════════════════════════
     PARALLAX SYSTEM — rAF-driven, multi-layer
     Layers:
       .hero-bg           background images (deep, slowest)
       .float-img         floating polaroid photos (mousemove + scroll drift)
       .dest-card-img img card cover images (subtle inner zoom-drift)
       .section-title     section headings (very subtle lift)
       [data-parallax]    any element with a custom speed attribute
  ═══════════════════════════════════════════════════════════════ */

  let _scrollY = window.scrollY;
  let _ticking  = false;

  // Build target list once after DOM is ready
  const _px = [];

  // Hero background images
  document.querySelectorAll('.hero-bg').forEach(el =>
    _px.push({ el, type: 'bg', speed: 0.38 })
  );

  // Custom data-parallax elements (authors can add data-parallax="0.2" to any el)
  document.querySelectorAll('[data-parallax]').forEach(el => {
    _px.push({
      el, type: 'custom',
      speed:  parseFloat(el.dataset.parallax)  || 0.2,
      speedX: parseFloat(el.dataset.parallaxX) || 0
    });
  });

  // Destination card cover images — subtle inner parallax
  document.querySelectorAll('.dest-card-img img').forEach(el =>
    _px.push({ el, type: 'card', speed: 0.1 })
  );

  // Section titles — very gentle upward float as you scroll past
  document.querySelectorAll('.section-title').forEach(el =>
    _px.push({ el, type: 'text', speed: 0.06 })
  );

  // City cards (home page grid)
  document.querySelectorAll('.city-card img').forEach(el =>
    _px.push({ el, type: 'card', speed: 0.08 })
  );

  function _runParallax() {
    const sy = _scrollY;
    const vh = window.innerHeight;

    _px.forEach(({ el, type, speed, speedX = 0 }) => {
      const rect   = el.getBoundingClientRect();
      if (rect.bottom < -100 || rect.top > vh + 100) return; // out of view

      const center = rect.top + rect.height / 2 - vh / 2; // distance from viewport center

      if (type === 'bg') {
        // Background moves slower → stays behind
        el.style.transform = `translateY(${center * speed}px) scale(1.14)`;

      } else if (type === 'card') {
        // Image inside card container shifts upward slightly
        el.style.transform = `translateY(${center * speed * -1}px) scale(1.06)`;

      } else if (type === 'text') {
        // Headings float up gently
        el.style.transform = `translateY(${center * speed * -1}px)`;

      } else if (type === 'custom') {
        const ty = center * speed  * -1;
        const tx = center * speedX * -1;
        el.style.transform = `translate(${tx}px, ${ty}px)`;
      }
    });

    _ticking = false;
  }

  window.addEventListener('scroll', () => {
    _scrollY = window.scrollY;
    if (!_ticking) {
      requestAnimationFrame(_runParallax);
      _ticking = true;
    }
  }, { passive: true });

  _runParallax(); // initial pass

  /* ── Floating image parallax (mousemove + gentle scroll drift) ── */
  const floats = document.querySelectorAll('.float-img, .auth-float-img');
  if (floats.length) {
    const depths = [0.018, 0.032, 0.024, 0.028, 0.020, 0.014, 0.026];
    // Separate per-float scroll-drift speeds so they move independently
    const scrollDrifts = [0.06, 0.10, 0.08, 0.12, 0.07, 0.05, 0.09];
    let mx = 0, my = 0, cx = 0, cy = 0;

    window.addEventListener('mousemove', e => {
      mx = e.clientX - window.innerWidth  / 2;
      my = e.clientY - window.innerHeight / 2;
    }, { passive: true });

    (function tickFloats() {
      cx += (mx - cx) * 0.06;
      cy += (my - cy) * 0.06;
      floats.forEach((el, i) => {
        const d   = depths[i % depths.length];
        const sd  = scrollDrifts[i % scrollDrifts.length];
        const r   = parseFloat(getComputedStyle(el).getPropertyValue('--r') || '0');
        // mousemove lateral drift + independent scroll drift per photo
        const tx  = cx * d;
        const ty  = cy * d - window.scrollY * sd * 0.5;
        el.style.transform = `translate(${tx}px, ${ty}px) rotate(${r}deg)`;
      });
      requestAnimationFrame(tickFloats);
    })();
  }

  /* ── Hero bg parallax (scroll) ───────────────────────────── */
  const heroBgs = document.querySelectorAll('.hero-bg');
  if (heroBgs.length) {
    window.addEventListener('scroll', () => {
      heroBgs.forEach(bg => {
        const hero = bg.closest('.hero');
        if (!hero) return;
        const rect = hero.getBoundingClientRect();
        if (rect.bottom < 0 || rect.top > window.innerHeight) return;
        bg.style.transform = `translateY(${rect.top / window.innerHeight * 40}px) scale(1.1)`;
      });
    }, { passive: true });
  }

  /* ── Rotating headline (framer-motion spring port) ─────────── */
  const wordContainer = document.getElementById('word-container');
  if (wordContainer) {
    const items = [...wordContainer.querySelectorAll('.rotate-word')];
    if (items.length) {
      let titleNumber = 0;

      function updateWords() {
        items.forEach((item, index) => {
          // Mirror framer-motion logic exactly:
          // index === titleNumber  → active  (y: 0,    opacity: 1)
          // index < titleNumber   → past    (y: -150%, opacity: 0)
          // index > titleNumber   → future  (y: +150%, opacity: 0) ← CSS default
          item.classList.remove('active', 'past');
          if (index === titleNumber) {
            item.classList.add('active');
          } else if (index < titleNumber) {
            item.classList.add('past');
          }
          // future: no class needed, CSS default handles it
        });
      }

      updateWords(); // show word 0 immediately

      setInterval(() => {
        titleNumber = titleNumber === items.length - 1 ? 0 : titleNumber + 1;
        updateWords();
      }, 2000);
    }
  }

  /* ── Hero city search filter ─────────────────────────────── */
  const heroSearch = document.getElementById('hero-search');
  const citiesGrid = document.getElementById('cities-grid');
  if (heroSearch && citiesGrid) {
    heroSearch.addEventListener('input', function () {
      const q = this.value.toLowerCase().trim();
      citiesGrid.querySelectorAll('.city-card').forEach(c => {
        c.style.display = (c.dataset.name || '').includes(q) ? '' : 'none';
      });
    });
  }

  /* ── Tabs ────────────────────────────────────────────────── */
  document.querySelectorAll('[data-tabs]').forEach(group => {
    const btns = group.querySelectorAll('.tab-btn');
    btns.forEach(btn => btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      group.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      const panel = group.querySelector(`[data-panel="${target}"]`);
      if (panel) panel.classList.add('active');
    }));
  });

  /* ── Scroll-reveal (IntersectionObserver) ────────────────── */
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

  document.querySelectorAll('.reveal').forEach((el, i) => {
    el.style.transitionDelay = `${i * 50}ms`;
    io.observe(el);
  });

  /* Auto-stagger cards in grids that aren't already .reveal */
  document.querySelectorAll('.post-grid, .grid-cities, .dashboard-grid').forEach(grid => {
    [...grid.children].forEach((child, i) => {
      if (!child.classList.contains('reveal')) {
        child.classList.add('reveal');
        child.style.transitionDelay = `${i * 60}ms`;
        io.observe(child);
      }
    });
  });

  /* booking-card directional stagger */
  document.querySelectorAll('.booking-card').forEach((card, i) => {
    if (!card.classList.contains('reveal')) {
      card.classList.add('reveal', i % 2 === 0 ? 'from-left' : 'from-right');
      io.observe(card);
    }
  });

  /* stat-card & dashboard-stat stagger */
  document.querySelectorAll('.stat-card, .dashboard-stat').forEach((card, i) => {
    if (!card.classList.contains('reveal')) {
      card.classList.add('reveal', 'scale-up');
      card.style.transitionDelay = `${i * 80}ms`;
      io.observe(card);
    }
  });

  /* review-item stagger */
  document.querySelectorAll('.review-item').forEach((item, i) => {
    if (!item.classList.contains('reveal')) {
      item.classList.add('reveal');
      item.style.transitionDelay = `${i * 90}ms`;
      io.observe(item);
    }
  });

  /* ── Count-up for stat numbers ───────────────────────────── */
  const countIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const raw = el.textContent.trim();
      const hasK = /k$/i.test(raw);
      const num = parseFloat(raw.replace(/[^0-9.]/g, ''));
      if (isNaN(num)) return;
      countIO.unobserve(el);
      const dur = 1200, t0 = performance.now();
      (function step(now) {
        const p = Math.min((now - t0) / dur, 1);
        const v = (1 - Math.pow(1 - p, 3)) * num;
        el.textContent = hasK ? (v >= 1 ? v.toFixed(1) + 'k' : Math.round(v * 1000) + '') : (num < 10 ? v.toFixed(1) : Math.round(v));
        if (p < 1) requestAnimationFrame(step); else el.textContent = raw;
      })(t0);
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.stat-value, .dashboard-stat-val').forEach(el => countIO.observe(el));

  /* ── Star picker ─────────────────────────────────────────── */
  document.querySelectorAll('.star-picker').forEach(picker => {
    const labels = [...picker.querySelectorAll('label')].reverse();
    picker.querySelectorAll('input').forEach(input => {
      input.addEventListener('change', () => {
        labels.forEach((l, i) => l.style.color = i < +input.value ? 'var(--secondary)' : '');
      });
    });
  });

  /* ── Carousel ────────────────────────────────────────────── */
  const carousel = document.getElementById('carousel');
  if (carousel) {
    let idx = 0;
    const slides = carousel.querySelectorAll('.carousel-slide');
    const total = slides.length;
    window.carouselNext = () => { idx = (idx + 1) % total; carousel.style.transform = `translateX(-${idx*100}%)`; };
    window.carouselPrev = () => { idx = (idx - 1 + total) % total; carousel.style.transform = `translateX(-${idx*100}%)`; };
    let auto = setInterval(window.carouselNext, 4500);
    carousel.addEventListener('mouseenter', () => clearInterval(auto));
    carousel.addEventListener('mouseleave', () => { auto = setInterval(window.carouselNext, 4500); });
  }

  /* ── Chat: auto-scroll + textarea resize ────────────────── */
  const msgs = document.getElementById('chat-messages');
  if (msgs) msgs.scrollTop = msgs.scrollHeight;
  const ta = document.querySelector('.chat-input-area textarea');
  if (ta) {
    ta.addEventListener('input', () => {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
    });
    ta.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = ta.closest('form');
        if (form) form.submit();
      }
    });
  }

  /* ── Like buttons (non-form, inline) ────────────────────── */
  document.querySelectorAll('.like-btn:not(form *)').forEach(btn => {
    btn.addEventListener('click', () => btn.classList.toggle('liked'));
  });

  /* ── Toast helper ────────────────────────────────────────── */
  window.showToast = (msg, type = 'info') => {
    const t = document.createElement('div');
    t.className = `alert alert-${type}`;
    t.style.cssText = 'position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;min-width:260px;max-width:380px;';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity='0'; t.style.transition='opacity .3s'; setTimeout(()=>t.remove(),350); }, 4000);
  };

  /* ── getCookie (CSRF) ────────────────────────────────────── */
  window.getCookie = name => {
    let v = null;
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '=')) v = decodeURIComponent(c.slice(name.length + 1));
    });
    return v;
  };

  /* ── toggleLike (called from Django templates) ───────────── */
  window.toggleLike = (postId, btn) => {
    fetch(`/posts/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
    })
    .then(r => r.json())
    .then(data => {
      const countEl = btn.querySelector('.like-count');
      const iconEl  = btn.querySelector('.like-icon');
      if (countEl) countEl.textContent = data.count;
      if (iconEl)  iconEl.textContent  = data.liked ? '❤️' : '🤍';
      btn.classList.toggle('liked', data.liked);
    })
    .catch(() => {});
  };

  /* ── Notification WebSocket ──────────────────────────────── */
  if (document.body.dataset.userId) {
    try {
      const ws = new WebSocket(`ws://${location.host}/ws/notifications/`);
      ws.onmessage = e => {
        const data = JSON.parse(e.data);
        showToast(data.message, data.type === 'booking' ? 'success' : 'info');
        const dot = document.getElementById('notif-dot');
        if (dot) dot.style.display = 'inline-flex';
      };
    } catch (_) {}
  }

  /* ── Chat WebSocket (initChat called from template) ─────── */
  window.initChat = (conversationId, currentUserId) => {
    const ws     = new WebSocket(`ws://${location.host}/ws/chat/${conversationId}/`);
    const msgsEl = document.getElementById('chat-messages');
    const input  = document.getElementById('chat-input');
    const sendBtn= document.getElementById('send-btn');
    if (!msgsEl || !input || !sendBtn) return;

    ws.onmessage = e => {
      appendMsg(JSON.parse(e.data));
      msgsEl.scrollTop = msgsEl.scrollHeight;
    };

    function send() {
      const txt = input.value.trim();
      if (!txt) return;
      ws.send(JSON.stringify({ message: txt }));
      input.value = '';
      if (input.tagName === 'TEXTAREA') { input.style.height = 'auto'; }
    }

    sendBtn.addEventListener('click', send);
    input.addEventListener('keypress', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });
    msgsEl.scrollTop = msgsEl.scrollHeight;

    function appendMsg(data) {
      const mine = data.sender_id == currentUserId;
      const div = document.createElement('div');
      div.className = `chat-message ${mine ? 'mine' : 'theirs'}`;
      div.innerHTML = `<div class="chat-bubble">${esc(data.message)}</div><div class="chat-time">${data.sender} · ${data.timestamp}</div>`;
      msgsEl.appendChild(div);
    }

    function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  };

}); /* end DOMContentLoaded */
