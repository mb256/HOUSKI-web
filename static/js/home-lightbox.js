// Picture-of-week lightbox: click the homepage thumbnail to view the
// full-size picture.
document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('picture-of-week-lightbox');
    if (!overlay) return;

    const img = overlay.querySelector('.lightbox-img');
    const closeBtn = overlay.querySelector('.lightbox-close');
    const btn = document.querySelector('.picture-of-week-btn');

    function open() {
        img.src = btn.dataset.full;
        overlay.hidden = false;
    }

    function close() {
        overlay.hidden = true;
        img.src = '';
    }

    if (btn) btn.addEventListener('click', open);
    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) close();
    });
    document.addEventListener('keydown', function (e) {
        if (!overlay.hidden && e.key === 'Escape') close();
    });
});
