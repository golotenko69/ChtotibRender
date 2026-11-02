(function () {
    "use strict";

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
                label.textContent = "✓ " + file.name + " (" + formatSize(file.size) + ")";
                var removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.textContent = "✕";
                removeBtn.setAttribute("aria-label", "Удалить файл");
                removeBtn.addEventListener("click", function () {
                    dt.items.remove(index);
                    input.files = dt.files;
                    render();
                });
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

    // Sticky header gains a solid/blurred background once the page scrolls
    // past the hero, matching the blueprint reference site.
    function initNavbarScroll() {
        var navbar = document.querySelector(".navbar");
        if (!navbar) return;
        function onScroll() {
            navbar.classList.toggle("is-scrolled", window.scrollY > 24);
        }
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    // FAQ accordion — single-open, animated via max-height in CSS.
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

    // Mobile nav toggle.
    function initMobileNav() {
        var burger = document.querySelector(".navbar__burger");
        var nav = document.querySelector(".navbar__nav");
        if (!burger || !nav) return;
        burger.addEventListener("click", function () {
            nav.classList.toggle("is-open");
        });
        nav.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () { nav.classList.remove("is-open"); });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-upload-zone]").forEach(initUploadZone);
        initNavbarScroll();
        initFaqAccordion();
        initMobileNav();

        // Auto-dismiss alerts after a few seconds.
        document.querySelectorAll(".alert").forEach(function (alertEl) {
            setTimeout(function () {
                alertEl.style.transition = "opacity .3s ease";
                alertEl.style.opacity = "0";
                setTimeout(function () { alertEl.remove(); }, 300);
            }, 6000);
        });
    });
})();
