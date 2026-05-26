document.addEventListener("DOMContentLoaded", function () {

    // ADD PRODUCT TOGGLE
    const addProductBtn = document.getElementById("addProductBtn");
    const addProductForm = document.getElementById("addProductForm");

    if (addProductBtn && addProductForm) {
        addProductBtn.addEventListener("click", function () {
            addProductForm.style.display =
                addProductForm.style.display === "block" ? "none" : "block";
        });
    }

    // CATEGORY HANDLING
    const selects = document.querySelectorAll("select[name='category']");

    selects.forEach((select) => {
        select.addEventListener("change", function () {
            const form = this.closest("form");
            if (!form) return;

            const input = form.querySelector("input[name='new_category']");
            if (!input) return;

            if (this.value === "__new__") {
                input.style.display = "block";
                input.required = true;
            } else {
                input.style.display = "none";
                input.required = false;
            }
        });
    });

    // DELETE CONFIRMATION
    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            if (!confirm("Delete this product?")) {
                e.preventDefault();
            }
        });
    });

    // CSRF helper
    function getCSRFToken() {
        return document.querySelector('[name=csrf-token]').content;
    }
    
    // AVAILABILITY TOGGLE
    window.toggleAvailability = function (itemId) {

        fetch(`/menu/toggle-availability/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json"
            }
        })
        .then(res => res.json())
        .then(data => {

            if (!data.success) return;

            const btn = document.querySelector(
                `.item-toggle[onclick*="${itemId}"]`
            );

            if (!btn) return;

            if (data.is_available) {
                btn.classList.remove("btn-danger");
                btn.classList.add("btn-success");
                btn.textContent = "Available";
            } else {
                btn.classList.remove("btn-success");
                btn.classList.add("btn-danger");
                btn.textContent = "Unavailable";
            }

            const card = btn.closest(".menu-item-card");
            if (card) {
                card.classList.toggle("item-available", data.is_available);
                card.classList.toggle("item-unavailable", !data.is_available);
            }

        })
        .catch(err => console.error(err));
    };
});