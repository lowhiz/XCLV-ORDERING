// ===========================
// CART AND ORDER MANAGEMENT
// ===========================
let cart = {}; // Track quantities by item ID

// Helper function to get category icon path
function getCategoryIcon(category) {
    // Map category names to icon filenames
    const iconMap = {
        'BEERS': 'beers.png',
        'COCKTAILS': 'cocktail.png',
        'SHOOTERS': 'shooter.png',
        'SINGLE SHOTS': 'shot.png',
        'MOCKTAILS': 'cocktail.png',
        'FRUITS': 'fruit.png',
        'BEVERAGES': 'soda.png',
        'FOOD': 'restaurant.png',
        'RUM': 'rum.png',
        'TEQUILA': 'tequila.png',
        'VODKA': 'vodka.png',
        'GIN': 'gin.png',
        'WINE': 'wine.png',
        'WHISKY/SCOTCH': 'vodka.png',
        'BRANDY/COGNAC': 'rum.png',
        'LIQUERS': 'rum.png',
    };

    const filename = iconMap[category.toUpperCase()] || 'cocktail.png';

    // Get the static URL base path from a static element or construct it
    // Assuming your static files are served from /static/
    return `/static/images/${filename}`;
}

// Restore previous order if available
document.addEventListener('DOMContentLoaded', function () {
    // Restore saved order
    const savedOrder = JSON.parse(sessionStorage.getItem('orderData') || '{}');
    if (savedOrder.items && Object.keys(savedOrder.items).length > 0) {
        savedOrder.items.forEach(item => {
            cart[item.id] = {
                id: item.id,
                name: item.name,
                price: parseFloat(item.unit_price || item.price) || 0,
                quantity: parseInt(item.quantity) || 0,
                category: item.category || ''
            };

            // Update quantity display in menu
            const qtySpan = document.querySelector(`.qty[data-item-id="${item.id}"]`);
            if (qtySpan) {
                qtySpan.textContent = cart[item.id].quantity;
            }
        });

        updateOrderSummary();
    }

    // Setup dropdown toggles
    setupDropdownToggles();

    // Setup menu listeners
    attachMenuListeners();

    // Setup modal listeners
    attachModalListeners();

    // Initialize order summary
    updateOrderSummary();
});


// ===========================
// DROPDOWN TOGGLE LOGIC
// ===========================
function setupDropdownToggles() {
    const dropdownHeaders = document.querySelectorAll('.dropdown-header');

    dropdownHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const categoryId = this.id.replace('Toggle', '');
            const dropdown = document.getElementById(categoryId + 'Dropdown');

            if (dropdown) {
                dropdown.classList.toggle('show');

                // Rotate arrow icon
                const arrow = this.querySelector('.dropdown-arrow');
                if (arrow) {
                    arrow.style.transform = dropdown.classList.contains('show')
                        ? 'rotate(180deg)'
                        : 'rotate(0deg)';
                }
            }
        });
    });
}


// ===========================
// QUANTITY MANAGEMENT
// ===========================
function changeQuantity(itemId, delta) {
    const itemCard = document.querySelector(`.item-card[data-item-id="${itemId}"]`);
    if (!itemCard) return;

    const itemName = itemCard.dataset.itemName;
    const itemPrice = parseFloat(itemCard.dataset.itemPrice);
    const itemCategory = itemCard.dataset.itemCategory;

    // Initialize if doesn't exist
    if (!cart[itemId]) {
        cart[itemId] = {
            id: itemId,
            name: itemName,
            price: itemPrice,
            quantity: 0,
            category: itemCategory
        };
    }

    // Update quantity
    cart[itemId].quantity = Math.max(0, cart[itemId].quantity + delta);

    // Remove from cart if quantity becomes 0
    if (cart[itemId].quantity === 0) {
        delete cart[itemId];
    }

    // Update all quantity displays for this item
    updateMenuQuantity(itemId);
    updateOrderSummary();
}

function updateMenuQuantity(itemId) {
    const qtySpans = document.querySelectorAll(`.qty[data-item-id="${itemId}"]`);
    const quantity = cart[itemId] ? cart[itemId].quantity : 0;

    qtySpans.forEach(span => {
        span.textContent = quantity;
    });
}


// ===========================
// ORDER SUMMARY
// ===========================
function updateOrderSummary() {
    const summaryList = document.getElementById('summaryList');
    const orderTotalElement = document.getElementById('order-total');

    if (!summaryList || !orderTotalElement) return;

    // Clear current summary
    summaryList.innerHTML = '';

    const cartItems = Object.values(cart).filter(item => item.quantity > 0);

    if (cartItems.length === 0) {
        summaryList.innerHTML = '<li class="text-muted">No items ordered yet.</li>';
        orderTotalElement.textContent = 'Total: ₱0.00';
        return;
    }

    // Create summary items
    cartItems.forEach(item => {
        const li = document.createElement('li');
        li.className = 'summary-item-card';
        li.dataset.itemId = item.id;

        const iconSrc = getCategoryIcon(item.category);

        li.innerHTML = `
            <div class="left">
                <img src="${iconSrc}" class="drink-icon" />
                <i class="bi bi-info-circle info-icon" data-item-id="${item.id}"></i>
                <p class="drink-title">${item.name}</p>
            </div>
            <div class="right">
                <button class="qty-btn minus" data-item-id="${item.id}">−</button>
                <span class="qty summary-qty">${item.quantity}</span>
                <button class="qty-btn plus" data-item-id="${item.id}">+</button>
            </div>
        `;

        summaryList.appendChild(li);
    });

    // Calculate and display total
    const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    orderTotalElement.textContent = `Total: ₱${total.toFixed(2)}`;

    // Reattach listeners for summary items
    attachSummaryListeners();
}

function attachSummaryListeners() {
    const summaryList = document.getElementById('summaryList');
    if (!summaryList) return;

    summaryList.querySelectorAll('.plus').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            changeQuantity(btn.dataset.itemId, 1);
        };
    });

    summaryList.querySelectorAll('.minus').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            changeQuantity(btn.dataset.itemId, -1);
        };
    });

    // Attach modal listeners for info icons in summary
    summaryList.querySelectorAll('.info-icon').forEach(icon => {
        icon.onclick = (e) => {
            e.stopPropagation();
            showModal(icon.dataset.itemId);
        };
    });
}


// ===========================
// MENU LISTENERS
// ===========================
function attachMenuListeners() {
    document.querySelectorAll('.item-card .plus').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            changeQuantity(btn.dataset.itemId, 1);
        };
    });

    document.querySelectorAll('.item-card .minus').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            changeQuantity(btn.dataset.itemId, -1);
        };
    });
}


// ===========================
// MODAL FOR ITEM DESCRIPTION
// ===========================
const itemModalOverlay = document.getElementById('itemModalOverlay');
const itemModalBody = document.querySelector('.item-modal-content .modal-body');
const modalCloseBtn = document.getElementById('modalCloseBtn');

function showModal(itemId) {
    const itemCard = document.querySelector(`.item-card[data-item-id="${itemId}"]`);
    if (!itemCard) return;

    const itemName = itemCard.dataset.itemName;
    const itemPrice = parseFloat(itemCard.dataset.itemPrice).toFixed(2);
    const itemDescription = itemCard.dataset.itemDescription || 'No description available.';
    const itemCategory = itemCard.dataset.itemCategory;

    const iconSrc = getCategoryIcon(itemCategory);

    itemModalBody.innerHTML = `
        <div class="modal-info-card">
            <div class="modal-item-header">
                <img src="${iconSrc}" class="drink-icon modal-icon" />
                <div class="modal-text-group">
                    <p class="modal-item-title">${itemName}</p>
                    <p class="modal-category">Category: ${itemCategory}</p>
                    <p class="modal-price">₱${itemPrice}</p>
                </div>
            </div>
            <div class="modal-description-section">
                <p class="modal-description-label">Description:</p>
                <p class="modal-description-text">${itemDescription}</p>
            </div>
        </div>
    `;

    itemModalOverlay.classList.add('show-modal');
    document.body.style.overflow = 'hidden';
}

function hideModal() {
    itemModalOverlay.classList.remove('show-modal');
    document.body.style.overflow = '';
}

if (modalCloseBtn) {
    modalCloseBtn.onclick = hideModal;
}

if (itemModalOverlay) {
    itemModalOverlay.onclick = (e) => {
        if (e.target === itemModalOverlay) {
            hideModal();
        }
    };
}

function attachModalListeners() {
    document.querySelectorAll('.info-icon').forEach(icon => {
        icon.onclick = (e) => {
            e.stopPropagation();
            showModal(icon.dataset.itemId);
        };
    });
}


// ===========================
// REDIRECT TO REVIEW PAGE
// ===========================
function redirectForReview() {
    const orderItems = Object.values(cart).filter(item => item.quantity > 0);

    if (orderItems.length === 0) {
        alert('No items to order! Please add items to your cart first.');
        return;
    }

    // Store cart data in session storage for the review page
    const menuData = document.getElementById('menu-data');
    sessionStorage.setItem('orderData', JSON.stringify({
        items: orderItems,
        table_id: menuData.dataset.tableId,
        table_display: menuData.dataset.tableDisplay
    }));

    // Redirect to review page
    window.location.href = '/menu/review/';
}
