(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + " Б";
        if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + " КБ";
        return (bytes / (1024 * 1024)).toFixed(1) + " МБ";
    }

    // DataTransfer-backed file list so users can remove individual files
    // before submitting; the underlying <input type="file"> stays the
    // source of truth submitted to the server, which re-validates anyway.
    function initUploadZone(zone) {
        var input = zone.querySelector("input[type=file]");
        var drop = zone.querySelector("[data-upload-drop]");
        var list = zone.querySelector("[data-upload-list]");
        if (!input || !drop || !list) return;

        var dt = new DataTransfer();

        function render() {
            list.innerHTML = "";
            Array.prototype.forEach.call(input.files, function (file, index) {
                var li = document.createElement("li");
                var label = document.createElement("span");
                label.textContent = "✓ " + file.name + " · " + formatSize(file.size);
                var removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.textContent = "✕";
                removeBtn.setAttribute("aria-label", "Удалить файл");
                removeBtn.addEventListener("click", function () {
                    dt.items.remove(index);
                    input.files = dt.files;
                    render();
                });
                li.style.animationDelay = index * 60 + "ms";
                li.appendChild(label);
                li.appendChild(removeBtn);
                list.appendChild(li);
            });
        }

        function addFiles(fileList) {
            Array.prototype.forEach.call(fileList, function (file) {
                dt.items.add(file);
            });
            input.files = dt.files;
            render();
        }

        input.addEventListener("change", function () {
            dt = new DataTransfer();
            Array.prototype.forEach.call(input.files, function (f) { dt.items.add(f); });
            render();
        });

        ["dragenter", "dragover"].forEach(function (evt) {
            drop.addEventListener(evt, function (e) {
                e.preventDefault();
                drop.classList.add("is-dragover");
            });
        });
        ["dragleave", "drop"].forEach(function (evt) {
            drop.addEventListener(evt, function (e) {
                e.preventDefault();
                drop.classList.remove("is-dragover");
            });
        });
        drop.addEventListener("drop", function (e) {
            if (e.dataTransfer && e.dataTransfer.files.length) {
                if (input.hasAttribute("multiple")) {
                    addFiles(e.dataTransfer.files);
                } else {
                    input.files = e.dataTransfer.files;
                    render();
                }
            }
        });
    }

    // Floating pill header: tints once the page scrolls, hides while
    // scrolling down and returns on the way up.
    function initNavbarScroll() {
        var navbar = document.querySelector(".navbar");
        if (!navbar) return;
        var lastY = window.scrollY;
        function onScroll() {
            var y = window.scrollY;
            navbar.classList.toggle("is-scrolled", y > 24);
            navbar.classList.toggle("is-hidden", y > 400 && y > lastY + 4);
            if (y < lastY - 4 || y < 400) navbar.classList.remove("is-hidden");
            lastY = y;
        }
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    // A glowing pill slides under whichever nav link is hovered.
    function initNavPill() {
        var nav = document.querySelector(".navbar__nav");
        var pill = nav && nav.querySelector(".navbar__pill");
        if (!pill) return;
        nav.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("mouseenter", function () {
                pill.style.width = link.offsetWidth + "px";
                pill.style.transform = "translateX(" + link.offsetLeft + "px)";
            });
        });
    }

    // FAQ accordion — single-open, animated via grid rows in CSS.
    function initFaqAccordion() {
        document.querySelectorAll(".faq-item__q").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var item = btn.closest(".faq-item");
                var wasOpen = item.classList.contains("is-open");
                item.closest(".faq-list").querySelectorAll(".faq-item.is-open").forEach(function (open) {
                    open.classList.remove("is-open");
                    open.querySelector(".faq-item__q").setAttribute("aria-expanded", "false");
                });
                if (!wasOpen) {
                    item.classList.add("is-open");
                    btn.setAttribute("aria-expanded", "true");
                }
            });
        });
    }

    // Reveal-on-scroll. Siblings revealed in the same batch get a stagger so
    // grids "print" in one card after another.
    function initReveal() {
        var targets = document.querySelectorAll("[data-reveal], [data-split], .extrude-line, .progress, [data-footer-word]");
        if (!("IntersectionObserver" in window) || reduceMotion) {
            targets.forEach(function (el) { el.classList.add("is-in"); });
            return;
        }
        function reveal(el) {
            el.classList.add("is-in");
            if (el.hasAttribute("data-reveal")) {
                var delay = parseFloat(getComputedStyle(el).transitionDelay) || 0;
                setTimeout(function () { el.removeAttribute("data-reveal"); }, 1100 + delay * 1000);
            }
        }
        var io = new IntersectionObserver(function (entries) {
            var batch = 0;
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                io.unobserve(el);
                // Fully clipped "print" items are invisible to the observer,
                // so their parent grid is watched and reveals them together.
                if (el.hasAttribute("data-print-host")) {
                    el.querySelectorAll(':scope > [data-reveal="print"]').forEach(reveal);
                    return;
                }
                if (el.classList.contains("product-card") && !el.style.getPropertyValue("--d")) {
                    el.style.setProperty("--d", (batch++ * 90) + "ms");
                }
                reveal(el);
            });
        }, { threshold: 0.14, rootMargin: "0px 0px -6% 0px" });
        targets.forEach(function (el) {
            if (el.getAttribute("data-reveal") === "print") {
                var host = el.parentElement;
                if (!host.hasAttribute("data-print-host")) {
                    host.setAttribute("data-print-host", "");
                    io.observe(host);
                }
                return;
            }
            io.observe(el);
        });
    }

    // Live layer counter in the hero chip, synced to the 9s print loop.
    function initLayerCounter() {
        var el = document.querySelector("[data-layer-counter]");
        if (!el || reduceMotion) return;
        var start = Date.now();
        setInterval(function () {
            if (document.hidden) return;
            var t = ((Date.now() - start) / 9000) % 1;
            el.textContent = Math.round(Math.min(1, t / 0.68) * 640);
        }, 250);
    }

    // Numbers count up when they scroll into view.
    // Thin "print progress" bar tracks how far the page is scrolled.
    function initProgress() {
        var bar = document.querySelector(".print-progress");
        if (!bar) return;
        var ticking = false;
        function update() {
            ticking = false;
            var max = document.documentElement.scrollHeight - window.innerHeight;
            bar.style.setProperty("--progress", max > 0 ? (window.scrollY / max).toFixed(4) : 0);
        }
        window.addEventListener("scroll", function () {
            if (!ticking) { ticking = true; requestAnimationFrame(update); }
        }, { passive: true });
        update();
    }

    function initCounters() {
        var els = document.querySelectorAll("[data-count]");
        if (!els.length || reduceMotion || !("IntersectionObserver" in window)) return;
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                var target = parseInt(el.getAttribute("data-count"), 10);
                var suffix = el.getAttribute("data-suffix") || "";
                var start = performance.now();
                (function tick(now) {
                    var t = Math.min(1, (now - start) / 1600);
                    var eased = 1 - Math.pow(1 - t, 4);
                    el.textContent = Math.round(target * eased) + suffix;
                    if (t < 1) requestAnimationFrame(tick);
                })(start);
                io.unobserve(el);
            });
        }, { threshold: 0.6 });
        els.forEach(function (el) { el.textContent = "0" + (el.getAttribute("data-suffix") || ""); io.observe(el); });
    }

    // Horizontal material rail: drag with the mouse, wheel scrolls sideways.
    function initRail() {
        document.querySelectorAll("[data-rail]").forEach(function (rail) {
            var down = false, startX = 0, startScroll = 0, moved = false;
            rail.addEventListener("mousedown", function (e) {
                down = true; moved = false; startX = e.pageX; startScroll = rail.scrollLeft;
            });
            window.addEventListener("mouseup", function () { down = false; rail.classList.remove("is-dragging"); });
            rail.addEventListener("mousemove", function (e) {
                if (!down) return;
                var dx = e.pageX - startX;
                if (Math.abs(dx) > 4) { moved = true; rail.classList.add("is-dragging"); }
                rail.scrollLeft = startScroll - dx;
            });
            rail.addEventListener("click", function (e) { if (moved) e.preventDefault(); }, true);
        });
    }

    function initFooterWord() {
        var el = document.querySelector("[data-footer-word]");
        if (!el) return;
        var letters = el.textContent.trim().split("");
        el.textContent = "";
        letters.forEach(function (ch, i) {
            var s = document.createElement("span");
            s.style.setProperty("--i", i);
            s.textContent = ch;
            el.appendChild(s);
        });
    }

    // Quantity stepper around a number input.
    function initQty() {
        document.querySelectorAll("[data-qty]").forEach(function (wrap) {
            var input = wrap.querySelector("input[type=number]");
            wrap.querySelectorAll("[data-step]").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    var min = parseInt(input.min || "1", 10);
                    var v = Math.max(min, (parseInt(input.value, 10) || min) + parseInt(btn.getAttribute("data-step"), 10));
                    input.value = v;
                    input.dispatchEvent(new Event("change", { bubbles: true }));
                });
            });
        });
    }

    // Product gallery: thumbnails swap the main image with a fade.
    function initGallery() {
        var main = document.querySelector("[data-gallery-main]");
        if (!main) return;
        document.querySelectorAll("[data-gallery-thumb]").forEach(function (thumb) {
            thumb.addEventListener("click", function () {
                document.querySelectorAll("[data-gallery-thumb]").forEach(function (t) { t.classList.remove("is-active"); });
                thumb.classList.add("is-active");
                main.style.opacity = "0";
                setTimeout(function () { main.src = thumb.getAttribute("data-gallery-thumb"); main.style.opacity = "1"; }, 200);
            });
        });
    }

    function initCartBump() {
        var count = document.querySelector(".navbar__cart-count");
        if (!count || !document.querySelector(".alert--success")) return;
        count.classList.add("is-bump");
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-upload-zone]").forEach(initUploadZone);
        initNavbarScroll();
        initNavPill();
        initFaqAccordion();
        initFooterWord();
        initReveal();
        initProgress();
        initLayerCounter();
        initCounters();
        initRail();
        initQty();
        initGallery();
        initCartBump();

        // Auto-dismiss alerts after a few seconds.
        document.querySelectorAll(".alert").forEach(function (alertEl) {
            setTimeout(function () {
                alertEl.style.transition = "opacity .4s ease, transform .4s ease";
                alertEl.style.opacity = "0";
                alertEl.style.transform = "translateX(40px)";
                setTimeout(function () { alertEl.remove(); }, 400);
            }, 6000);
        });
    });
})();
