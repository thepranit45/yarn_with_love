
document.addEventListener('DOMContentLoaded', function () {
    // 1. SCROLL ANIMATIONS (Intersection Observer)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Elements to animate
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => {
        el.classList.add('fade-up'); // Initial class from style.css
        observer.observe(el);
    });

    // 2. HERO PARALLAX EFFECT
    const heroSection = document.querySelector('.hero-section-new');
    const heroFlowers = document.querySelectorAll('.hero-flower-top, .hero-decoration-left, .hero-decoration-right');

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        if (scrolled < 800) { // Only animate when hero is likely visible
            heroFlowers.forEach((flower, index) => {
                const speed = (index + 1) * 0.1;
                flower.style.transform = `translateY(${scrolled * speed}px) rotate(${scrolled * 0.05}deg)`;
            });
        }
    });
});
