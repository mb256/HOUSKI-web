// Board (nástěnka) picture lightbox: click a thumbnail to view it full size,
// step through the other images of the same post with the < / > buttons.
document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('board-lightbox');
    if (!overlay) return;

    const img = overlay.querySelector('.lightbox-img');
    const prevBtn = overlay.querySelector('.lightbox-prev');
    const nextBtn = overlay.querySelector('.lightbox-next');
    const closeBtn = overlay.querySelector('.lightbox-close');

    // Group thumbnails by post so prev/next only cycles within one post.
    const groups = {};
    document.querySelectorAll('.post-image-btn').forEach(function (btn) {
        const group = btn.dataset.group;
        if (!groups[group]) groups[group] = [];
        groups[group].push(btn.dataset.full);
        btn.addEventListener('click', function () {
            open(group, groups[group].indexOf(btn.dataset.full));
        });
    });

    let currentGroup = null;
    let currentIndex = 0;

    function open(group, index) {
        currentGroup = group;
        currentIndex = index;
        render();
        overlay.hidden = false;
    }

    function render() {
        const images = groups[currentGroup];
        img.src = images[currentIndex];
        const multiple = images.length > 1;
        prevBtn.hidden = !multiple;
        nextBtn.hidden = !multiple;
    }

    function step(delta) {
        const images = groups[currentGroup];
        currentIndex = (currentIndex + delta + images.length) % images.length;
        render();
    }

    function close() {
        overlay.hidden = true;
        img.src = '';
    }

    prevBtn.addEventListener('click', function () { step(-1); });
    nextBtn.addEventListener('click', function () { step(1); });
    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) close();
    });
    document.addEventListener('keydown', function (e) {
        if (overlay.hidden) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowLeft') step(-1);
        else if (e.key === 'ArrowRight') step(1);
    });
});
