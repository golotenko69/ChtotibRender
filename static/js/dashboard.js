(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Panels and cards fade up as they enter the viewport.
    function initReveal() {
        var els = document.querySelectorAll(".dash-reveal, .dash-panel, .dash-stat-card, .dash-queue-card, .dash-category-card, .dash-table-wrap");
        els.forEach(function (el) { el.classList.add("dash-reveal"); });
        if (reduceMotion || !("IntersectionObserver" in window)) {
            els.forEach(function (el) { el.classList.add("is-in"); });
            return;
        }
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-in");
                io.unobserve(entry.target);
            });
        }, { threshold: 0.08 });
        els.forEach(function (el) { io.observe(el); });
    }

    // Table rows slide in one after another.
    function initRows() {
        document.querySelectorAll(".dash-table tbody").forEach(function (tbody) {
            Array.prototype.forEach.call(tbody.rows, function (row, i) {
                row.style.setProperty("--i", Math.min(i, 20));
            });
        });
    }

    // Stat numbers count up from zero.
    function initCounters() {
        if (reduceMotion) return;
        document.querySelectorAll("[data-count]").forEach(function (el) {
            var target = parseInt(el.getAttribute("data-count"), 10) || 0;
            if (!target) return;
            var start = performance.now() + 200;
            el.textContent = "0";
            (function tick(now) {
                var t = Math.min(1, Math.max(0, (now - start) / 1300));
                el.textContent = Math.round(target * (1 - Math.pow(1 - t, 4)));
                if (t < 1) requestAnimationFrame(tick);
            })(performance.now());
        });
    }

    function initClock() {
        var el = document.querySelector("[data-clock]");
        var greet = document.querySelector("[data-greeting]");
        function pad(n) { return n < 10 ? "0" + n : n; }
        function update() {
            var d = new Date();
            if (el) el.textContent = pad(d.getHours()) + ":" + pad(d.getMinutes()) + " · " + pad(d.getDate()) + "." + pad(d.getMonth() + 1);
            if (greet) {
                var h = d.getHours();
                greet.textContent = h < 6 ? "Доброй ночи" : h < 12 ? "Доброе утро" : h < 18 ? "Добрый день" : "Добрый вечер";
            }
        }
        update();
        setInterval(update, 30000);
    }

    document.addEventListener("DOMContentLoaded", function () {
        initReveal();
        initRows();
        initCounters();
        initClock();

        // Live preview for single-image file inputs (product/category images).
        document.querySelectorAll("[data-preview-input]").forEach(function (input) {
            var targetId = input.getAttribute("data-preview-input");
            var target = document.getElementById(targetId);
            if (!target) return;
            input.addEventListener("change", function () {
                var file = input.files && input.files[0];
                if (!file) return;
                var reader = new FileReader();
                reader.onload = function (e) {
                    target.src = e.target.result;
                    target.style.display = "block";
                };
                reader.readAsDataURL(file);
            });
        });

        // Auto-dismiss alerts.
        document.querySelectorAll(".dash-alert").forEach(function (el) {
            setTimeout(function () {
                el.style.transition = "opacity .4s ease, transform .4s ease";
                el.style.opacity = "0";
                el.style.transform = "translateX(40px)";
                setTimeout(function () { el.remove(); }, 400);
            }, 6000);
        });

        // Close mobile sidebar when a nav link is tapped or outside is clicked.
        var sidebar = document.querySelector(".dash-sidebar");
        document.querySelectorAll(".dash-nav__link").forEach(function (link) {
            link.addEventListener("click", function () { sidebar.classList.remove("is-open"); });
        });
        document.addEventListener("click", function (e) {
            if (!sidebar || !sidebar.classList.contains("is-open")) return;
            if (!sidebar.contains(e.target) && !e.target.closest(".dash-topbar__burger")) sidebar.classList.remove("is-open");
        });
    });
})();
