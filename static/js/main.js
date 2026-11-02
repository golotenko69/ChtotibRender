(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

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

    // Wraps each word of [data-split] headings so they rise one by one.
    function initSplitWords() {
        document.querySelectorAll("[data-split]").forEach(function (el) {
            var i = 0;
            function walk(node) {
                Array.prototype.slice.call(node.childNodes).forEach(function (child) {
                    if (child.nodeType === 3) {
                        var parts = child.textContent.split(/(\s+)/);
                        var frag = document.createDocumentFragment();
                        parts.forEach(function (part) {
                            if (!part) return;
                            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
                            var w = document.createElement("span");
                            w.className = "w";
                            var inner = document.createElement("span");
                            inner.style.setProperty("--i", i++);
                            inner.textContent = part;
                            w.appendChild(inner);
                            frag.appendChild(w);
                        });
                        child.parentNode.replaceChild(frag, child);
                    } else if (child.nodeType === 1) {
                        walk(child);
                    }
                });
            }
            walk(el);
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

    // Scroll-linked effects batched into one rAF: print progress bar,
    // parallax orbs and the manifesto line/words.
    function initScrollFx() {
        var bar = document.querySelector(".print-progress");
        var parallax = reduceMotion ? [] : Array.prototype.slice.call(document.querySelectorAll("[data-parallax]"));
        var manifesto = document.querySelector("[data-manifesto]");
        var words = [];
        var line = manifesto && manifesto.querySelector(".manifesto__line path");

        if (manifesto) {
            var text = manifesto.querySelector("[data-words]");
            Array.prototype.slice.call(text.childNodes).forEach(function (node) {
                var frag = document.createDocumentFragment();
                var extraCls = node.nodeType === 1 ? " " + node.className : "";
                node.textContent.split(/(\s+)/).forEach(function (part) {
                    if (!part) return;
                    if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
                    var s = document.createElement("span");
                    s.className = "word" + extraCls;
                    s.textContent = part;
                    words.push(s);
                    frag.appendChild(s);
                });
                text.replaceChild(frag, node);
            });
        }

        var ticking = false;
        function update() {
            ticking = false;
            var y = window.scrollY;
            var vh = window.innerHeight;
            var max = document.documentElement.scrollHeight - vh;
            if (bar) bar.style.setProperty("--progress", max > 0 ? (y / max).toFixed(4) : 0);
            parallax.forEach(function (el) {
                el.style.transform = "translate3d(0," + (y * parseFloat(el.getAttribute("data-parallax"))).toFixed(1) + "px,0)";
            });
            if (manifesto) {
                var r = manifesto.getBoundingClientRect();
                var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height * 0.8)));
                if (reduceMotion) p = 1;
                if (line) line.style.setProperty("--p", p.toFixed(3));
                var lit = Math.round(p * words.length * 1.15);
                words.forEach(function (w, idx) { w.classList.toggle("is-lit", idx < lit); });
            }
        }
        window.addEventListener("scroll", function () {
            if (!ticking) { ticking = true; requestAnimationFrame(update); }
        }, { passive: true });
        window.addEventListener("resize", update);
        update();
    }

    // Hero rig leans toward the cursor for a sense of depth.
    function initHeroTilt() {
        var stage = document.querySelector("[data-hero-stage]");
        if (!stage || reduceMotion || !finePointer) return;
        var rig = stage.querySelector(".hero__rig");
        var hero = stage.closest(".hero");
        hero.addEventListener("mousemove", function (e) {
            var r = stage.getBoundingClientRect();
            var dx = (e.clientX - (r.left + r.width / 2)) / r.width;
            var dy = (e.clientY - (r.top + r.height / 2)) / r.height;
            rig.style.setProperty("--rx", (dx * 14).toFixed(2) + "deg");
            rig.style.setProperty("--ry", (-dy * 10).toFixed(2) + "deg");
        });
        hero.addEventListener("mouseleave", function () {
            rig.style.setProperty("--rx", "0deg");
            rig.style.setProperty("--ry", "0deg");
        });
    }

    // Live layer counter in the hero chip, synced to the 9s print loop.
    function initLayerCounter() {
        var el = document.querySelector("[data-layer-counter]");
        if (!el || reduceMotion) return;
        var start = performance.now();
        function frame(now) {
            var t = ((now - start) / 9000) % 1;
            var p = Math.min(1, t / 0.68);
            el.textContent = Math.round(p * 640);
            requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }

    // Product cards tilt in 3D and carry a glare that follows the cursor.
    function initTilt() {
        if (reduceMotion || !finePointer) return;
        document.querySelectorAll("[data-tilt]").forEach(function (card) {
            card.addEventListener("mousemove", function (e) {
                var r = card.getBoundingClientRect();
                var px = (e.clientX - r.left) / r.width;
                var py = (e.clientY - r.top) / r.height;
                card.classList.add("is-tilting");
                card.style.setProperty("--ry", ((px - 0.5) * 12).toFixed(2) + "deg");
                card.style.setProperty("--rx", ((0.5 - py) * 10).toFixed(2) + "deg");
                card.style.setProperty("--gx", (px * 100).toFixed(1) + "%");
                card.style.setProperty("--gy", (py * 100).toFixed(1) + "%");
            });
            card.addEventListener("mouseleave", function () {
                card.classList.remove("is-tilting");
                card.style.setProperty("--rx", "0deg");
                card.style.setProperty("--ry", "0deg");
            });
        });
    }

    // Soft spotlight that tracks the pointer across glass cards.
    function initSpotlight() {
        if (!finePointer) return;
        document.querySelectorAll("[data-spotlight]").forEach(function (el) {
            el.addEventListener("mousemove", function (e) {
                var r = el.getBoundingClientRect();
                el.style.setProperty("--gx", (e.clientX - r.left) + "px");
                el.style.setProperty("--gy", (e.clientY - r.top) + "px");
            });
        });
    }

    // Buttons drift toward the cursor a little.
    function initMagnetic() {
        if (reduceMotion || !finePointer) return;
        document.querySelectorAll("[data-magnetic]").forEach(function (btn) {
            btn.addEventListener("mousemove", function (e) {
                var r = btn.getBoundingClientRect();
                var x = e.clientX - (r.left + r.width / 2);
                var y = e.clientY - (r.top + r.height / 2);
                btn.style.transform = "translate(" + (x * 0.18).toFixed(1) + "px," + (y * 0.28).toFixed(1) + "px)";
            });
            btn.addEventListener("mouseleave", function () { btn.style.transform = ""; });
        });
    }

    function initRipple() {
        document.addEventListener("pointerdown", function (e) {
            var btn = e.target.closest(".btn");
            if (!btn || reduceMotion) return;
            var r = btn.getBoundingClientRect();
            var size = Math.max(r.width, r.height);
            var dot = document.createElement("span");
            dot.className = "ripple";
            dot.style.width = dot.style.height = size + "px";
            dot.style.left = (e.clientX - r.left - size / 2) + "px";
            dot.style.top = (e.clientY - r.top - size / 2) + "px";
            btn.appendChild(dot);
            setTimeout(function () { dot.remove(); }, 700);
        });
    }

    function initCursorGlow() {
        var glow = document.querySelector(".cursor-glow");
        if (!glow || !finePointer || reduceMotion) { if (glow) glow.remove(); return; }
        var tx = -999, ty = -999, cx = tx, cy = ty, running = false;
        function loop() {
            cx += (tx - cx) * 0.12;
            cy += (ty - cy) * 0.12;
            glow.style.setProperty("--cx", cx.toFixed(1) + "px");
            glow.style.setProperty("--cy", cy.toFixed(1) + "px");
            if (Math.abs(tx - cx) > 0.5 || Math.abs(ty - cy) > 0.5) requestAnimationFrame(loop);
            else running = false;
        }
        window.addEventListener("mousemove", function (e) {
            tx = e.clientX; ty = e.clientY;
            if (cx === -999) { cx = tx; cy = ty; }
            if (!running) { running = true; requestAnimationFrame(loop); }
        }, { passive: true });
    }

    // Numbers count up when they scroll into view.
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

    function initConfetti() {
        var host = document.querySelector("[data-confetti]");
        if (!host || reduceMotion) return;
        var colors = ["#FF8A3D", "#FFB066", "#5FD4C4", "#9BE7DC", "#EEF2F1"];
        for (var i = 0; i < 60; i++) {
            var c = document.createElement("i");
            c.style.left = Math.random() * 100 + "%";
            c.style.background = colors[i % colors.length];
            c.style.animationDelay = (Math.random() * 1.2) + "s";
            c.style.animationDuration = (2.4 + Math.random() * 1.8) + "s";
            c.style.transform = "rotate(" + Math.random() * 360 + "deg)";
            host.appendChild(c);
        }
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
        initSplitWords();
        initFooterWord();
        initReveal();
        initScrollFx();
        initHeroTilt();
        initLayerCounter();
        initTilt();
        initSpotlight();
        initMagnetic();
        initRipple();
        initCursorGlow();
        initCounters();
        initRail();
        initQty();
        initGallery();
        initConfetti();
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
