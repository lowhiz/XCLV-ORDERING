document.addEventListener("DOMContentLoaded", () => {
    // --- Dropdown toggle ---
    const dropdownHeaders = document.querySelectorAll(".dropdown-header");
    if (dropdownHeaders) {
        dropdownHeaders.forEach(header => {
            header.addEventListener("click", () => {
                const slug = header.id.replace("Toggle", "");
                const dropdown = document.getElementById(slug + "Dropdown");
                if (dropdown) dropdown.classList.toggle("show");
            });
        });
    }

    const itemModalOverlay = document.getElementById("itemModalOverlay");
    const modalBody = itemModalOverlay.querySelector(".modal-body");
    const modalCloseBtn = document.getElementById("modalCloseBtn");

    // --- Attach modal listeners ---
    document.querySelectorAll(".info-icon").forEach(icon => {
        icon.addEventListener("click", (e) => {
            e.stopPropagation();

            const itemId = icon.dataset.itemId;
            const itemCard = document.querySelector(`.item-card[data-item="${itemId}"]`);
            if (!itemCard) return;

            // Get item data
            const name = itemCard.querySelector(".drink-title")?.textContent || "";
            const imgSrc = itemCard.querySelector("img.drink-icon")?.src || "/static/images/cocktail.png";
            const price = itemCard.querySelector(".qty-btn.plus")?.dataset.itemPrice || "0";
            const category = itemCard.dataset.category || "Cocktails"; // Add this in your HTML
            const description = itemCard.dataset.description || "No description";

            // Insert into modal
            modalBody.innerHTML = `
                <div class="modal-info-card">
                    <div class="modal-item-header">
                        <img src="${imgSrc}" class="drink-icon modal-icon" />
                        <div class="modal-text-group">
                            <p class="modal-item-title">${name}</p>
                            <p class="modal-category">Category: ${category}</p>
                            <p class="modal-price">Php ${price}</p>
                        </div>
                    </div>
                    <div class="modal-description-section">
                        <p class="modal-description-label">Description:</p>
                        <p class="modal-description-text">${description}</p>
                    </div>
                </div>
            `;

            // Show modal
            itemModalOverlay.classList.add("show-modal");
            document.body.style.overflow = "hidden";
        });
    });

    // --- Close modal ---
    modalCloseBtn.addEventListener("click", () => {
        itemModalOverlay.classList.remove("show-modal");
        document.body.style.overflow = "";
    });

    itemModalOverlay.addEventListener("click", (e) => {
        if (e.target === itemModalOverlay) {
            itemModalOverlay.classList.remove("show-modal");
            document.body.style.overflow = "";
        }
    });
});
