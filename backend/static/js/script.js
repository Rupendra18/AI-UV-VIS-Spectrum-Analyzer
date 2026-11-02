/* ==========================================================================
   AI UV-Vis Spectrum Analyzer - Interactive UI & Theme Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {

    // ── Theme & Accent Color Controller ─────────────────────────────────────
    initThemeAndAccent();

    // ── Sidebar Toggle ────────────────────────────────────────────────────────
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });
    }

    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('active')
            && !sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
            sidebar.classList.remove('active');
        }
    });

    // ── Drag & Drop CSV Upload Handling ─────────────────────────────────────
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');

    if (dropzone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
            dropzone.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
            document.body.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
        });

        ['dragenter', 'dragover'].forEach(evt => {
            dropzone.addEventListener(evt, () => dropzone.classList.add('drag-over'));
        });

        ['dragleave', 'drop'].forEach(evt => {
            dropzone.addEventListener(evt, () => dropzone.classList.remove('drag-over'));
        });

        dropzone.addEventListener('drop', function(e) {
            const files = e.dataTransfer.files;
            if (files.length > 0 && fileInput && uploadForm) {
                const file = files[0];
                if (!file.name.toLowerCase().endsWith('.csv')) {
                    showToast('Only CSV files with Wavelength and Absorbance are supported.', 'danger', 'fa-exclamation-triangle');
                    return;
                }
                fileInput.files = files;
                document.getElementById('upload-icon-fa').className = 'fas fa-spinner fa-spin';
                document.getElementById('upload-title').textContent = 'Processing: ' + file.name;
                showToast('Uploading ' + file.name + ' for AI Analysis...', 'info', 'fa-cloud-upload-alt');
                uploadForm.submit();
            }
        });
    }

    // ── Toast Container Setup ─────────────────────────────────────────────────
    if (!document.getElementById('toast-container')) {
        const tc = document.createElement('div');
        tc.id = 'toast-container';
        tc.className = 'toast-container';
        document.body.appendChild(tc);
    }

    // ── Auto-dismiss Flash Alerts into Toasts ─────────────────────────────
    const alerts = document.querySelectorAll('.flash-messages .alert');
    alerts.forEach(alert => {
        const text = alert.textContent.trim();
        const isSuccess = alert.classList.contains('alert-success');
        showToast(text, isSuccess ? 'success' : 'danger', isSuccess ? 'fa-check-circle' : 'fa-exclamation-circle');
    });

    // ── Animate KPI Numbers on Dashboard Load ──────────────────────────────
    const statValues = document.querySelectorAll('.stat-value-anim');
    statValues.forEach(el => {
        const target = parseFloat(el.getAttribute('data-target') || '0');
        if (!isNaN(target) && target > 0) {
            animateValue(el, 0, target, 1000);
        }
    });

});

// ── Theme & Accent Helpers ───────────────────────────────────────────────────

function initThemeAndAccent() {
    const savedTheme = localStorage.getItem('spectrum_theme') || 'dark';
    const savedAccent = localStorage.getItem('spectrum_accent') || 'blue';

    document.documentElement.setAttribute('data-theme', savedTheme);
    document.documentElement.setAttribute('data-accent', savedAccent);

    updateAccentDotUI(savedAccent);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('spectrum_theme', next);
    updateThemeIcon(next);

    // Sync theme with Plotly if graph exists
    if (typeof Plotly !== 'undefined' && document.getElementById('spectrum-graph')) {
        const bg = next === 'light' ? 'rgba(255,255,255,0)' : 'rgba(0,0,0,0)';
        const fontColor = next === 'light' ? '#0f172a' : '#94a3b8';
        const gridColor = next === 'light' ? 'rgba(0,0,0,0.08)' : 'rgba(51,65,85,0.5)';
        Plotly.relayout('spectrum-graph', {
            'font.color': fontColor,
            'xaxis.gridcolor': gridColor,
            'yaxis.gridcolor': gridColor,
            'paper_bgcolor': bg,
            'plot_bgcolor': bg
        });
    }

    showToast(`Switched to ${next.toUpperCase()} theme`, 'info', next === 'dark' ? 'fa-moon' : 'fa-sun');
}

function setAccent(color) {
    document.documentElement.setAttribute('data-accent', color);
    localStorage.setItem('spectrum_accent', color);
    updateAccentDotUI(color);
    showToast(`Accent color updated to ${color}`, 'info', 'fa-palette');
}

function updateAccentDotUI(color) {
    document.querySelectorAll('.accent-dot').forEach(dot => {
        dot.classList.toggle('active', dot.getAttribute('data-accent-val') === color);
    });
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
        btn.innerHTML = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }
}

// ── Toast Notification System ───────────────────────────────────────────────

function showToast(message, type = 'info', icon = 'fa-info-circle') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fas ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}

// ── KPI Number Count Up Animation ─────────────────────────────────────────

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = (progress * (end - start) + start);
        obj.textContent = end % 1 === 0 ? Math.floor(current) : current.toFixed(2);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.textContent = end % 1 === 0 ? end : end.toFixed(2);
        }
    };
    window.requestAnimationFrame(step);
}
