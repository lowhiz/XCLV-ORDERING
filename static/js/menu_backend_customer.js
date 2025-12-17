
document.addEventListener('DOMContentLoaded', function () {
    // Restore previous order if available
    const savedOrder = JSON.parse(sessionStorage.getItem('orderData') || '{}');

    if (savedOrder.items && Object.keys(savedOrder.items).length > 0) {
        savedOrder.items.forEach(item => {
            // Update cart object
            cart[item.id] = {
                id: item.id,
                name: item.name,
                price: parseFloat(item.unit_price || item.price) || 0,
                quantity: parseInt(item.quantity) || 0
            };

            // Update quantity display in menu
            const qtySpan = document.getElementById(`quantity-${item.id}`);
            if (qtySpan) {
                qtySpan.textContent = cart[item.id].quantity;
            }
        });

        // Update order summary
        updateOrderSummary();
    }
});

// Grab table info from HTML data attributes
let cart = {}; // Track quantities by item ID

function increaseQuantity(itemId) {
  const qtyEl = document.getElementById(`quantity-${itemId}`);
  const currentDisplayed = qtyEl ? parseInt(qtyEl.textContent) || 0 : 0;

  // Read data safely from the DOM to avoid quote issues
  const itemCard = document.querySelector(`.item-card[data-item-id="${itemId}"]`);
  const itemName = itemCard?.dataset.name || '';
  const itemPrice = parseFloat(itemCard?.dataset.price || '0');

  // Initialize if doesn't exist
  if (!cart[itemId]) {
    cart[itemId] = {
      id: itemId,
      name: itemName,
      price: itemPrice,
      quantity: currentDisplayed,
    };
  }

  // Increase quantity
  cart[itemId].quantity++;

  // Update displays
  updateMenuQuantity(itemId);
  updateOrderSummary();
  updateCartDisplay();
}

function decreaseQuantity(itemId) {
  // Only decrease if item exists and quantity > 0
  if (cart[itemId] && cart[itemId].quantity > 0) {
    cart[itemId].quantity--;

    // Remove from cart if quantity becomes 0
    if (cart[itemId].quantity === 0) {
      delete cart[itemId];
    }

    // Update displays
    updateMenuQuantity(itemId);
    updateOrderSummary();
    updateCartDisplay();
  }
}

function updateMenuQuantity(itemId) {
  const quantityElement = document.getElementById("quantity-" + itemId);
  if (quantityElement) {
    quantityElement.textContent = cart[itemId] ? cart[itemId].quantity : 0;
  }
}

function updateOrderSummary() {
    const orderItemsContainer = document.getElementById("order-items");
    orderItemsContainer.innerHTML = "";

    const cartItems = Object.values(cart).filter(item => item.quantity > 0);

    if (cartItems.length === 0) return;

        const iconMap = {
            "Cocktails": "cocktail.png",
            "Mocktails": "mocktail.png",
            "Beers": "beer.png",
            "Shooters": "shooter.png",
            "Single Shots": "shot.png",
            "Fruits": "fruit.png",
            "Beverages": "soda.png",
            "Food": "restaurant.png",
            "Rum": "rum.png",
            "Whisky/Scotch": "whisky.png",
            "Liquers": "liqueur.png",
            "Tequila": "tequila.png",
            "Vodka": "vodka.png",
            "Gin": "gin.png",
            "Wine": "wine.png"
        };

        cartItems.forEach(item => {
        const originalCard = document.querySelector(`.item-card[data-item-id="${item.id}"]`);
        if (!originalCard) return;

        const name = originalCard.dataset.name;
        const category = originalCard.dataset.category;
        const price = originalCard.dataset.price;
        const description = originalCard.dataset.description;
        const staticPath = originalCard.dataset.staticPath; // keep this

        // Map category to icon file
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

        const iconFilename = iconMap[category] || "cocktail.png";
        const iconUrl = `${staticPath}${iconFilename}`;

        const li = document.createElement("li");
        li.className = "summary-item-card";
        li.innerHTML = `
            <div class="left d-flex align-items-center gap-2">
                <img src="${iconUrl}" class="drink-icon" alt="${name}">
                <i class="bi bi-info-circle info-icon" data-item-id="${item.id}"></i>
                <p class="drink-title mb-0">${name}</p>
            </div>
            <div class="right d-flex align-items-center gap-2">
                <button class="qty-btn minus btn btn-sm btn-outline-secondary" data-item-id="${item.id}">−</button>
                <span class="qty summary-qty">${item.quantity}</span>
                <button class="qty-btn plus btn btn-sm btn-outline-primary" data-item-id="${item.id}" data-item-price="${price}">+</button>
            </div>
        `;
        orderItemsContainer.appendChild(li);

        // Modal popup for info icon
        const infoIcon = li.querySelector(".info-icon");
        infoIcon.addEventListener("click", e => {
            e.stopPropagation();
            const modalOverlay = document.getElementById("itemModalOverlay");
            const modalBody = document.getElementById("modalBody");
            modalBody.innerHTML = `
                <div class="modal-info-card">
                    <div class="modal-item-header">
                        <img src="${iconUrl}" class="drink-icon modal-icon" alt="${name}">
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
            modalOverlay.classList.add("show-modal");
            document.body.style.overflow = "hidden";
        });
    });
}

document.getElementById("modalCloseBtn").addEventListener("click", () => {
    const modalOverlay = document.getElementById("itemModalOverlay");
    modalOverlay.classList.remove("show-modal");
    document.body.style.overflow = "";
});

document.getElementById("itemModalOverlay").addEventListener("click", (e) => {
    if (e.target === e.currentTarget) {
        e.currentTarget.classList.remove("show-modal");
        document.body.style.overflow = "";
    }
});

// Delegated handlers for summary plus/minus buttons
document.addEventListener('DOMContentLoaded', function () {
  const orderItemsContainer = document.getElementById('order-items');

  // Use event delegation because the buttons are added dynamically
  orderItemsContainer.addEventListener('click', function (e) {
    const btn = e.target.closest('.qty-btn');
    if (!btn) return;

    const itemId = btn.dataset.itemId;
    if (!itemId) return;

    if (btn.classList.contains('plus')) {
      // Reuse main increase logic
      increaseQuantity(itemId);
    } else if (btn.classList.contains('minus')) {
      // Reuse main decrease logic
      decreaseQuantity(itemId);
    }

    // Update the summary quantity for this specific item row
    const summaryItem = btn.closest('.summary-item-card');
    const summaryQty = summaryItem?.querySelector('.summary-qty');
    if (summaryQty) {
      summaryQty.textContent = cart[itemId] ? cart[itemId].quantity : 0;
    }
  });
});



function updateCartDisplay() {
  const cartElement = document.getElementById("cart");
  const cartCount = document.getElementById("cart-count");
}

function placeOrder() {
  const orderItems = Object.values(cart).filter((item) => item.quantity > 0);

  if (orderItems.length === 0) {
    alert("No items to order!");
    return;
  }

  fetch("/menu/order/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}",
    },
    body: JSON.stringify({
      items: orderItems,
      table_id: "{{ table_id }}",
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Order placed successfully!");

        // Reset cart and quantities
        const oldCart = Object.keys(cart);
        cart = {};
        oldCart.forEach((itemId) => {
          updateMenuQuantity(itemId);
        });
        updateOrderSummary();
        updateCartDisplay();
      } else {
        alert("Error placing order: " + data.error);
      }
    })
    .catch((error) => {
      alert("Network error. Please try again.");
    });
}

function redirectForReview() {
  const orderItems = Object.values(cart).filter((item) => item.quantity > 0);

  if (orderItems.length === 0) {
    alert("No items to order! Please add items to your cart first.");
    return;
  }

  // Store cart data in session storage for the review page
  const menuData = document.getElementById("menu-data");
  sessionStorage.setItem(
    "orderData",
    JSON.stringify({
      items: orderItems,
      table_id: menuData.dataset.tableId,
      table_display: menuData.dataset.tableDisplay,
    })
  );

  // Redirect to review page
  window.location.href = "/menu/review/";
}

// Initialize order summary on page load
document.addEventListener("DOMContentLoaded", function () {
  updateOrderSummary();
});
