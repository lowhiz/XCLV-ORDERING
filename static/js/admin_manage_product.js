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
});

// ===========================
// INVENTORY: AVAILABILITY TOGGLE
// ===========================

async function toggleAvailability(itemId) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    try {
        const res = await fetch(`/menu/toggle-availability/${itemId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
        });

        if (!res.ok) {
            console.error('Toggle request failed:', res.status);
            return;
        }

        const data = await res.json();

        if (data.success) {
            // Update the card's data attribute so the next modal open reads the new state
            const card = document.querySelector(`.menu-item-card[data-item-id="${itemId}"]`);

            // New: Implementation of the Internal Inventory API needs the
            // toggle button element, then update its style classes based
            // on its availability state
            const toggleBtn = card.querySelector('.item-toggle');
            card.dataset.itemAvailable = data.is_available ? 'true' : 'false';

            // Swap the card's unavailable CSS class
            if (data.is_available) {
                card.classList.remove('item-unavailable');
                card.classList.add('item-available');
                toggleBtn.classList.remove('btn-danger');
                toggleBtn.classList.add('btn-success');

            } else {
                card.classList.remove('item-available');
                card.classList.add('item-unavailable');
                toggleBtn.classList.remove('btn-success');
                toggleBtn.classList.add('btn-danger');
            }

            // Re-render only when this item's modal is currently open
            const isModalOpen = itemModalOverlay.classList.contains('show-modal');
            const activeItemId = itemModalOverlay.dataset.activeItemId;
            if (isModalOpen && activeItemId === String(itemId)) {
                showModal(itemId);
            }
        }

    } catch (err) {
        console.error('Error toggling availability:', err);
    }
}
