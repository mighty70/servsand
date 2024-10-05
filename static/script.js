document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById('theme-toggle');

    // Toggle theme
    toggle.addEventListener('change', () => {
        if (toggle.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {
            toggle.checked = true;
        }
    }

    // Fetch PC statuses dynamically
    setInterval(fetchStatus, 5000);

    function fetchStatus() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                document.querySelector('.pc1 .status-text').textContent = data.pc1.status;
                document.getElementById('pc1-time').textContent = data.pc1.time || '--:--';

                document.querySelector('.pc2 .status-text').textContent = data.pc2.status;
                document.getElementById('pc2-time').textContent = data.pc2.time || '--:--';
            })
            .catch(err => console.error('Error fetching status:', err));
    }
});
