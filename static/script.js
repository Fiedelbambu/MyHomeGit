function toggleDetails(id, hash, project) {
    const details = document.getElementById(id);

    // Wenn bereits geladen → einfach sichtbar/unsichtbar toggeln
    if (details.innerHTML.trim() !== '') {
        details.classList.toggle('show');
        return;
    }

    const lineLimit = document.getElementById('lineLimit').value;
    const textOnly = document.getElementById('textOnly').checked;
    const hideBinary = document.getElementById('hideBinary').checked;

    fetch(`/log/${project}/${hash}?limit=${lineLimit}&textOnly=${textOnly}&hideBinary=${hideBinary}`)
        .then(res => res.text())
        .then(data => {
            details.innerHTML = `<pre><code class='language-diff'>${data}</code></pre>`;
            details.classList.add('show'); // Animation anzeigen
            if (window.Prism) {
                Prism.highlightAll();
            }
        });
}

document.addEventListener("DOMContentLoaded", function () {
    // Toggle Filter Panel
    const filterToggle = document.getElementById("filterToggle");
    const filterPanel = document.getElementById("filterPanel");
    if (filterToggle && filterPanel) {
        filterToggle.addEventListener("click", () => {
            filterPanel.style.display = filterPanel.style.display === "none" ? "block" : "none";
        });
    }

    // Toggle Tools Panel
    const toggleBtn = document.getElementById("toggleTools");
    const toolsPanel = document.getElementById("toolsPanel");
    if (toggleBtn && toolsPanel) {
        toggleBtn.addEventListener("click", () => {
            toolsPanel.style.display = toolsPanel.style.display === "none" ? "block" : "none";
        });
    }
});


function toggleFilter() {
    const panel = document.getElementById('filterPanel');
    panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    // Initialwerte aus localStorage setzen
    if (localStorage.getItem("lineLimit")) {
        document.getElementById('lineLimit').value = localStorage.getItem("lineLimit");
    }
    if (localStorage.getItem("textOnly")) {
        document.getElementById('textOnly').checked = localStorage.getItem("textOnly") === "true";
    }
    if (localStorage.getItem("hideBinary")) {
        document.getElementById('hideBinary').checked = localStorage.getItem("hideBinary") === "true";
    }

    // Bei Änderung speichern und Seite neuladen
    document.getElementById('lineLimit').addEventListener('change', () => {
        localStorage.setItem("lineLimit", document.getElementById('lineLimit').value);
        location.reload();
    });

    document.getElementById('textOnly').addEventListener('change', () => {
        localStorage.setItem("textOnly", document.getElementById('textOnly').checked);
        location.reload();
    });

    document.getElementById('hideBinary').addEventListener('change', () => {
        localStorage.setItem("hideBinary", document.getElementById('hideBinary').checked);
        location.reload();
    });

    // Zahnrad-Button
    const filterBtn = document.getElementById("filterToggle");
    if (filterBtn) {
        filterBtn.addEventListener("click", toggleFilter);
    }
});
