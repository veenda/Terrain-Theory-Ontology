document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Handle Form Submission (Loading State)
    var diagnoseForm = document.querySelector(".diagnose-form");
    
    if (diagnoseForm) {
        diagnoseForm.addEventListener("submit", function () {
            var submitButton = diagnoseForm.querySelector("button[type='submit']");
            
            if (submitButton) {
                // Simpan teks asli
                submitButton.dataset.originalText = submitButton.innerText;
                
                // Ubah jadi loading
                submitButton.disabled = true;
                submitButton.innerHTML = "⏳ Analyzing Terrain...";
                submitButton.style.opacity = "0.8";
                submitButton.style.cursor = "wait";
            }
        });
    }

    // 2. Smooth Scrolling untuk link anchor (jika ada)
    var links = document.querySelectorAll('a[href^="#"]');
    links.forEach(function (link) {
        link.addEventListener("click", function (event) {
            var href = link.getAttribute("href");
            if (!href || href.length < 2) return;
            
            var target = document.querySelector(href);
            if (target) {
                event.preventDefault();
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    // 3. Efek Fade In sederhana untuk hasil
    var results = document.querySelector('.disease-results');
    if (results) {
        results.style.opacity = 0;
        results.style.transition = 'opacity 0.8s ease-in';
        setTimeout(() => {
            results.style.opacity = 1;
        }, 100);
    }
});