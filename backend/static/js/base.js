function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

document.addEventListener('click', function (e) {
    const sidebar = document.getElementById('sidebar');
    const toggle = e.target.closest('.sidebar-toggle, .mobile-menu-btn');
    if (sidebar && sidebar.classList.contains('open') && !toggle && !e.target.closest('#sidebar')) {
        sidebar.classList.remove('open');
    }
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.remove('open');
    }
});
