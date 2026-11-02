(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
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
                el.style.transition = "opacity .3s ease";
                el.style.opacity = "0";
                setTimeout(function () { el.remove(); }, 300);
            }, 6000);
        });

        // Close mobile sidebar when a nav link is tapped.
        document.querySelectorAll(".dash-nav__link").forEach(function (link) {
            link.addEventListener("click", function () {
                document.querySelector(".dash-sidebar").classList.remove("is-open");
            });
        });
    });
})();
