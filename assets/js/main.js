/* ───── Mala Muerte — shared interactions ───── */

// 1. Lenis smooth scroll ---------------------------------------------------
function initLenis() {
  if (typeof Lenis === 'undefined') return null;
  const lenis = new Lenis({
    duration: 1.1,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
    smoothTouch: false,
  });
  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);

  // Sync with GSAP ScrollTrigger if loaded
  if (typeof ScrollTrigger !== 'undefined') {
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
  }
  return lenis;
}

// 2. Header scroll state ---------------------------------------------------
function initHeader() {
  const header = document.querySelector('.site-header');
  if (!header) return;
  const onScroll = () => {
    header.classList.toggle('is-scrolled', window.scrollY > 24);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

// 3. Mobile nav toggle -----------------------------------------------------
function initMobileNav() {
  const toggle = document.querySelector('.site-header__toggle');
  const nav    = document.querySelector('.site-nav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('is-open', !open);
    document.body.style.overflow = !open ? 'hidden' : '';
  });
  nav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      toggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
      document.body.style.overflow = '';
    });
  });
}

// 4. Reveal on scroll (IntersectionObserver) -------------------------------
function initReveals() {
  const targets = document.querySelectorAll('.reveal, [data-reveal]');
  if (!targets.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -80px 0px' });
  targets.forEach((t) => io.observe(t));
}

// 5. GSAP parallax on hero image ------------------------------------------
function initHeroParallax() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
  const heroMedia = document.querySelector('.hero__media');
  if (!heroMedia) return;
  gsap.to(heroMedia, {
    yPercent: 18,
    ease: 'none',
    scrollTrigger: {
      trigger: '.hero',
      start: 'top top',
      end: 'bottom top',
      scrub: true,
    },
  });
}

// 6. Story-rail word-by-word reveal ---------------------------------------
function initStoryReveal() {
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
  document.querySelectorAll('[data-word-reveal]').forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map((w) => `<span class="word"><span class="word__inner">${w}</span></span>`).join(' ');
    gsap.from(el.querySelectorAll('.word__inner'), {
      yPercent: 110,
      stagger: 0.04,
      duration: 0.9,
      ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 80%' },
    });
  });
}

// 7. Horizontal team track — drag-to-scroll (no wheel hijack) -------------
function initHorizontalScroll() {
  const track = document.querySelector('[data-hscroll]');
  if (!track) return;
  let isDown = false, startX = 0, startScroll = 0;
  track.addEventListener('pointerdown', (e) => {
    isDown = true;
    track.setPointerCapture(e.pointerId);
    startX = e.clientX;
    startScroll = track.scrollLeft;
    track.style.cursor = 'grabbing';
  });
  track.addEventListener('pointermove', (e) => {
    if (!isDown) return;
    track.scrollLeft = startScroll - (e.clientX - startX);
  });
  ['pointerup','pointercancel','pointerleave'].forEach((ev) =>
    track.addEventListener(ev, () => { isDown = false; track.style.cursor = ''; })
  );
}

// 8. Reservation form (decorative) ----------------------------------------
function initReservationForm() {
  const form = document.querySelector('[data-reservation-form]');
  const modal = document.querySelector('[data-reservation-modal]');
  if (!form || !modal) return;

  let lastFocus = null;

  const openModal = () => {
    lastFocus = document.activeElement;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    const first = modal.querySelector('[data-close-modal], button, a');
    first?.focus();
  };

  const closeModal = () => {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    form.reset();
    lastFocus?.focus();
  };

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    openModal();
  });

  modal.querySelectorAll('[data-close-modal]').forEach((btn) => {
    btn.addEventListener('click', closeModal);
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal();
  });
}

// 9. Current year in footer -----------------------------------------------
function initYear() {
  document.querySelectorAll('[data-year]').forEach((el) => {
    el.textContent = new Date().getFullYear();
  });
}

// 10. Team card flip (hover / tap) ----------------------------------------
function initTeamFlip() {
  document.querySelectorAll('.team-card').forEach((card) => {
    card.addEventListener('click', () => {
      card.classList.toggle('is-flipped');
    });
  });
}

// 11. Lightbox for atmosphere tiles ---------------------------------------
function initLightbox() {
  const overlay = document.querySelector('[data-lightbox-overlay]');
  const img     = document.querySelector('[data-lightbox-img]');
  const cap     = document.querySelector('[data-lightbox-caption]');
  const tiles   = document.querySelectorAll('[data-lightbox]');
  if (!overlay || !img || !tiles.length) return;

  let lastFocus = null;

  const open = (tile) => {
    lastFocus = document.activeElement;
    img.src = tile.dataset.src;
    img.alt = tile.querySelector('img')?.alt || '';
    cap.textContent = tile.dataset.caption || '';
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    overlay.querySelector('[data-lightbox-close]')?.focus();
    document.body.style.overflow = 'hidden';
  };

  const close = () => {
    overlay.classList.remove('is-open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    lastFocus?.focus();
  };

  tiles.forEach((t) => t.addEventListener('click', () => open(t)));
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay || e.target.matches('[data-lightbox-close]')) close();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) close();
  });
}

// ─── Boot ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initLenis();
  initHeader();
  initMobileNav();
  initReveals();
  initHeroParallax();
  initStoryReveal();
  initHorizontalScroll();
  initReservationForm();
  initYear();
  initTeamFlip();
  initLightbox();
});
