document.addEventListener("DOMContentLoaded", () => {

    // ------------------------------
    // CATEGORY → ICON MAP
    // ------------------------------
    const iconMap = {
        "Cocktails": "cocktail.png",
        "Mocktails": "cocktail.png",
        "Beers": "cocktail.png",
        "Shooters": "shooter.png",
        "Single Shots": "shot.png",
        "Fruits": "fruit.png",
        "Beverages": "soda.png",
        "Food": "restaurant.png",
        "Rum": "rum.png",
        "Whisky/Scotch": "rum.png",
        "Liquers": "rum.png",
        "Tequila": "tequila.png",
        "Vodka": "vodka.png",
        "Gin": "gin.png",
        "Wine": "gin.png"
    };

    // ------------------------------
    // SET ICONS FOR ALL ITEMS
    // ------------------------------
    document.querySelectorAll(".item-card").forEach(card => {
        const category = card.dataset.category;
        const iconImg = card.querySelector(".drink-icon");
        const staticPath = card.dataset.staticPath;

        if (iconImg) {
            const filename = iconMap[category] || "cocktail.png";
            iconImg.src = staticPath + filename;
        }
    });

    // ------------------------------
    // DROPDOWN TOGGLE
    // ------------------------------
    const dropdownHeaders = document.querySelectorAll(".dropdown-header");
    dropdownHeaders.forEach(header => {
        header.addEventListener("click", () => {
            const slug = header.id.replace("Toggle", "");
            const dropdown = document.getElementById(slug + "Dropdown");
            if (dropdown) dropdown.classList.toggle("show");
        });
    });

    // ------------------------------
    // MODAL OPEN
    // ------------------------------
    const itemModalOverlay = document.getElementById("itemModalOverlay");
    const modalBody = itemModalOverlay.querySelector(".modal-body");
    const modalCloseBtn = document.getElementById("modalCloseBtn");

    document.querySelectorAll(".info-icon").forEach(icon => {
        icon.addEventListener("click", (e) => {
            e.stopPropagation();

            const itemId = icon.dataset.itemId;
            const itemCard = document.querySelector(`.item-card[data-item-id="${itemId}"]`);
            if (!itemCard) return;

            const name = itemCard.dataset.name || "";
            const category = itemCard.dataset.category || "Cocktails";
            const price = itemCard.dataset.price || "0";
            const description = itemCard.dataset.description || "No description";
            const staticPath = itemCard.dataset.staticPath;

            const imgFilename = iconMap[category] || "cocktail.png";
            const imgSrc = staticPath + imgFilename;

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

            itemModalOverlay.classList.add("show-modal");
            document.body.style.overflow = "hidden";
        });
    });

    // ------------------------------
    // MODAL CLOSE
    // ------------------------------
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
