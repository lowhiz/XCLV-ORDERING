document.addEventListener("DOMContentLoaded", () => {
    const reviewBtn = document.querySelector(".review-order-btn");
    reviewBtn.addEventListener("click", () => {
        const orderItems = Object.values(cart).filter((item) => item.quantity > 0);

        if (orderItems.length === 0) {
            alert("No items to order! Please add items to your cart first.");
            return;
        }

        const menuData = document.getElementById("menu-data");
        sessionStorage.setItem(
            "orderData",
            JSON.stringify({
                items: orderItems,
                table_id: menuData.dataset.tableId,
                table_display: menuData.dataset.tableDisplay,
            })
        );

        window.location.href = "/menu/review/";
    });
    const summaryList = document.getElementById("summaryList");
    const itemModalOverlay = document.getElementById("itemModalOverlay");
    const itemModalBody = document.querySelector(".modal-body");
    const modalCloseBtn = document.getElementById("modalCloseBtn");

    let cart = {};

    // ----------------- CART FUNCTIONS -----------------
    function increaseQuantity(itemId) {
        const itemCard = document.querySelector(`.item-card[data-item-id="${itemId}"]`);
        if (!itemCard) return;

        const name = itemCard.dataset.name;
        const price = parseFloat(itemCard.querySelector(".qty-btn.plus")?.dataset.itemPrice || 0);
        const description = itemCard.dataset.description || "No description available";
        const category = itemCard.dataset.category || "Uncategorized";

        if (!cart[itemId]) {
            cart[itemId] = {
                id: itemId,
                name,
                price,
                description,
                category,
                quantity: 0
            };
        }

        cart[itemId].quantity++;
        updateMenuQuantity(itemId);
        updateOrderSummary();
    }

    function decreaseQuantity(itemId) {
        if (cart[itemId]) {
            cart[itemId].quantity--;
            if (cart[itemId].quantity <= 0) delete cart[itemId];
            updateMenuQuantity(itemId);
            updateOrderSummary();
        }
    }

    function updateMenuQuantity(itemId) {
        const qtySpan = document.getElementById(`quantity-${itemId}`);
        qtySpan.textContent = cart[itemId] ? cart[itemId].quantity : 0;
    }

    // ----------------- ORDER SUMMARY -----------------
    function updateOrderSummary() {
        summaryList.innerHTML = "";
        const items = Object.values(cart);

        if (items.length === 0) {
            summaryList.innerHTML = "<li>No items in order.</li>";
            return;
        }

        items.forEach(item => {
            const itemCard = document.querySelector(`.item-card[data-item-id="${item.id}"] img.drink-icon`);
            const imgSrc = itemCard ? itemCard.src : "/static/images/cocktail.png";

            const li = document.createElement("li");
            li.className = "summary-item-card";
            li.dataset.itemId = item.id;
            li.dataset.name = item.name;
            li.dataset.price = item.price.toFixed(2); // two decimals here
            li.dataset.category = item.category;
            li.dataset.description = item.description;

            li.innerHTML = `
                <div class="left">
                    <img src="${imgSrc}" class="drink-icon" />
                    <i class="bi bi-info-circle info-icon"></i>
                    <p class="drink-title">${item.name}</p>
                </div>
                <div class="right">
                    <button class="qty-btn minus" data-item-id="${item.id}">−</button>
                    <span class="qty summary-qty">${item.quantity}</span>
                    <button class="qty-btn plus" data-item-id="${item.id}" data-item-price="${item.price}">+</button>
                </div>
            `;
            summaryList.appendChild(li);
        });

        attachSummaryListeners();
        attachInfoListeners();
    }

    // ----------------- ATTACH SUMMARY BUTTONS -----------------
    function attachSummaryListeners() {
        document.querySelectorAll(".summary-item-card .plus").forEach(btn => {
            btn.onclick = () => increaseQuantity(btn.dataset.itemId);
        });

        document.querySelectorAll(".summary-item-card .minus").forEach(btn => {
            btn.onclick = () => decreaseQuantity(btn.dataset.itemId);
        });
    }

    // ----------------- INFO MODAL LISTENERS -----------------
    function attachInfoListeners() {
        document.querySelectorAll(".info-icon").forEach(icon => {
            icon.addEventListener("click", (e) => {
                e.stopPropagation();

                const itemCard = icon.closest(".item-card, .summary-item-card");
                if (!itemCard) return;

                // Get correct price from plus button if exists
                const plusBtn = itemCard.querySelector(".qty-btn.plus");
                const rawPrice = plusBtn?.dataset.itemPrice || itemCard.dataset.price || 0;
                const price = parseFloat(rawPrice).toFixed(2); // <-- TWO DECIMALS

                const name = itemCard.dataset.name || "No name";
                const category = itemCard.dataset.category || "No category";
                const description = itemCard.dataset.description || "No description";
                const imgSrc = itemCard.querySelector("img.drink-icon")?.src || "/static/images/cocktail.png";

                // Show modal
                showModal({ name, imgSrc, price, category, description });
            });
        });
    }

    // ----------------- MODAL -----------------
    function showModal({ name, imgSrc, price, category, description }) {
        itemModalBody.innerHTML = `
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
    }

    function closeModal() {
        itemModalOverlay.classList.remove("show-modal");
        document.body.style.overflow = "";
    }

    modalCloseBtn.onclick = closeModal;
    itemModalOverlay.onclick = (e) => {
        if (e.target === itemModalOverlay) closeModal();
    };

    // ----------------- INITIAL ATTACH FOR MENU CARDS -----------------
    document.querySelectorAll(".item-card .plus").forEach(btn => {
        btn.addEventListener("click", () => increaseQuantity(btn.dataset.itemId));
    });

    document.querySelectorAll(".item-card .minus").forEach(btn => {
        btn.addEventListener("click", () => decreaseQuantity(btn.dataset.itemId));
    });

    attachInfoListeners();
    updateOrderSummary();
    
});