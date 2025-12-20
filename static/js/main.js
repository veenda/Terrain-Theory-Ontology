document.addEventListener("DOMContentLoaded", function () {
    
    // 1. LOGIKA CASCADING DROPDOWN
    const catSelect = document.getElementById("category_select");
    const diseaseSelect = document.getElementById("disease_id");
    const btnSubmit = document.getElementById("btnSubmit");

    if (catSelect && diseaseSelect && typeof categoriesData !== 'undefined') {
        
        // Saat Kategori (Dropdown 1) berubah
        catSelect.addEventListener("change", function() {
            const selectedIndex = this.value; // Ini adalah index array (0, 1, 2...)
            const category = categoriesData[selectedIndex];

            // Reset Dropdown 2
            diseaseSelect.innerHTML = '<option value="" disabled selected>-- Select Specific Condition --</option>';
            diseaseSelect.disabled = false;
            btnSubmit.disabled = true; // Matikan tombol submit dulu

            // Isi Dropdown 2 dengan penyakit dari kategori yg dipilih
            if (category && category.diseases) {
                category.diseases.forEach(function(disease) {
                    const option = document.createElement("option");
                    option.value = disease.id;
                    option.textContent = disease.name;
                    diseaseSelect.appendChild(option);
                });
            }
        });

        // Saat Penyakit (Dropdown 2) berubah
        diseaseSelect.addEventListener("change", function() {
            if (this.value) {
                btnSubmit.disabled = false; // Baru nyalakan tombol submit
            }
        });
    }

    // 2. Loading State (Sama seperti sebelumnya)
    var diagnoseForm = document.querySelector(".diagnose-form");
    if (diagnoseForm) {
        diagnoseForm.addEventListener("submit", function () {
            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = "⏳ Generating Protocol...";
                btnSubmit.style.opacity = "0.8";
                btnSubmit.style.cursor = "wait";
            }
        });
    }
});