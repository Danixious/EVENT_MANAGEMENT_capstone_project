// main.js — EventIQ core interactions

document.addEventListener('DOMContentLoaded', () => {

    // ── Navbar scroll shadow ───────────────────────────────────────────────
    const navbar = document.getElementById('navbar');
    if (navbar) {
        const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 20);
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // ── Mobile hamburger ───────────────────────────────────────────────────
    const hamburger = document.getElementById('hamburger');
    const navLinks  = document.getElementById('navLinks');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            const isOpen = navLinks.classList.toggle('is-open');
            hamburger.setAttribute('aria-expanded', isOpen);
            // Animate bars
            const bars = hamburger.querySelectorAll('span');
            if (isOpen) {
                bars[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                bars[1].style.opacity   = '0';
                bars[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
            } else {
                bars.forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
            }
        });

        // Close nav on outside click
        document.addEventListener('click', (e) => {
            if (!navbar.contains(e.target)) {
                navLinks.classList.remove('is-open');
                hamburger.setAttribute('aria-expanded', 'false');
                hamburger.querySelectorAll('span').forEach(b => {
                    b.style.transform = ''; b.style.opacity = '';
                });
            }
        });
    }

    // ── Smooth scroll for anchor links ────────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const id = anchor.getAttribute('href').slice(1);
            const target = document.getElementById(id);
            if (target) {
                e.preventDefault();
                const offset = 72;
                const top = target.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: 'smooth' });
                // Close mobile menu if open
                if (navLinks) navLinks.classList.remove('is-open');
            }
        });
    });

    // ── Intersection observer for fade-in animations ───────────────────────
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll('.step-card, .feat-card, .loc-card, .venue-card, .risk-item, .rec-card')
        .forEach(el => observer.observe(el));

    // ── Counter animation for stat numbers ────────────────────────────────
    function animateCounter(el, target, duration = 1200) {
        const startTime = performance.now();
        const start = 0;
        const isFloat = target % 1 !== 0;

        const tick = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
            const value = start + (target - start) * eased;
            el.textContent = isFloat ? value.toFixed(1) : Math.round(value).toLocaleString('en-IN');
            if (progress < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }

    // Apply to result page numbers if present
    document.querySelectorAll('[data-counter]').forEach(el => {
        const val = parseFloat(el.dataset.counter);
        if (!isNaN(val)) {
            const counterObserver = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    animateCounter(el, val);
                    counterObserver.disconnect();
                }
            });
            counterObserver.observe(el);
        }
    });

});

// ── Utility: format INR ───────────────────────────────────────────────────
function formatINR(amount) {
    if (amount >= 10000000) return '₹' + (amount / 10000000).toFixed(1) + ' Cr';
    if (amount >= 100000)   return '₹' + (amount / 100000).toFixed(1) + ' L';
    if (amount >= 1000)     return '₹' + (amount / 1000).toFixed(0) + 'K';
    return '₹' + amount.toLocaleString('en-IN');
}

// ── Utility: debounce ─────────────────────────────────────────────────────
function debounce(fn, wait) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), wait); };
}

// Export for use in other modules
window.EventIQ = { formatINR, debounce };