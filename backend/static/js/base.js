function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

function updateNotificationBadge() {
    fetch('/notificacoes/unread-count/')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('notif-badge');
            if (badge) {
                if (data.count > 0) {
                    badge.style.display = 'flex';
                    badge.textContent = data.count > 99 ? '99+' : data.count;
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(() => {});
}

document.addEventListener('DOMContentLoaded', function() {
    updateNotificationBadge();
    setInterval(updateNotificationBadge, 60000);
});

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
