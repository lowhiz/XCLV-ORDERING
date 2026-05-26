// ===========================
// ADMIN VIEW MENU - MODAL FUNCTIONALITY
// ===========================

// Helper function to get category icon path
function getCategoryIcon(category) {
    // Map category names to icon filenames
    const iconMap = {
        'BEERS': 'beers.png',
        'COCKTAILS': 'cocktails.png',
        'SHOOTERS': 'shooters.png',
        'SINGLE SHOTS': 'shots.png',
        'MOCKTAILS': 'cocktails.png',
        'FRUITS': 'fruits.png',
        'BEVERAGES': 'sodas.png',
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

// Modal elements
const itemModalOverlay = document.getElementById('itemModalOverlay');
const itemModalBody = document.querySelector('.item-modal-content .modal-body');
const modalCloseBtn = document.getElementById('modalCloseBtn');

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM Content Loaded');
    console.log('Modal overlay:', itemModalOverlay);
    console.log('Modal body:', itemModalBody);
    console.log('Close button:', modalCloseBtn);

    attachModalListeners();
});

// ===========================
// MODAL FOR ITEM DESCRIPTION
// ===========================

function showModal(itemId) {
    console.log('showModal called with itemId:', itemId);

    // Find the menu item card with the matching item ID
    const menuItemCard = document.querySelector(`.menu-item-card[data-item-id="${itemId}"]`)

    if (!menuItemCard) {
        console.error('Menu item not found for ID:', itemId);
        return;
    }

    console.log('Menu item card found:', menuItemCard);

    // Get item data from data attributes
    const itemName = menuItemCard.dataset.itemName;
    const itemPrice = parseFloat(menuItemCard.dataset.itemPrice).toFixed(2);
    const itemDescription = menuItemCard.dataset.itemDescription || 'No description available.';
    const itemCategory = menuItemCard.dataset.itemCategory;
    const itemImage = getCategoryIcon(itemCategory);
    // ↓ new: read availability from the card's data attribute
    const isAvailable = menuItemCard.dataset.itemAvailable === 'true';

    console.log('Item data:', { itemName, itemPrice, itemDescription, itemCategory, itemImage });

    // Populate modal body with item information
    itemModalBody.innerHTML = `
        <div class="modal-info-card">
            <div class="modal-item-header">
                <img src="${itemImage}" class="drink-icon modal-icon" alt="${itemName}" />
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

            <!-- ↓ new: availability section -->
            <div class="modal-availability-section">
                <div class="availability-status-row">
                    <span class="availability-label">Availability:</span>
                    <span class="availability-badge ${isAvailable ? 'badge-available' : 'badge-unavailable'}">
                        ${isAvailable ? 'Available' : 'Out of Stock'}
                    </span>
                </div>
                <button
                    class="availability-toggle-btn ${isAvailable ? 'btn-mark-oos' : 'btn-mark-available'}"
                    onclick="toggleAvailability(${itemId})">
                    ${isAvailable ? 'MARK AS OUT OF STOCK' : 'MARK AS AVAILABLE'}
                </button>
            </div>
        </div>
    `;

    // Append Edit & Delete controls (Edit opens the existing edit modal, Delete submits to admin-delete-product)
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        const controlsHtml = `
            <div class="d-flex justify-content-center container">
                <div class="row w-100 g-2 mt-2">
                    <div class="col">
                        <button class="btn btn-primary admin-grey-button w-100 fw-bold" data-bs-toggle="modal" data-bs-target="#editModal${itemId}">EDIT ITEM</button>
                    </div>
                    <div class="col">
                        <form method="POST" action="/menu/admin-delete-product/${itemId}/" onsubmit="return confirm('Delete this product?');">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                            <button type="submit" class="btn btn-danger w-100 fw-bold">DELETE ITEM</button>
                        </form>
                    </div>
                </div>
            </div>
        `;

        itemModalBody.insertAdjacentHTML('beforeend', controlsHtml);
    } catch (err) {
        console.error('Error appending modal controls:', err);
    }

    // Show the modal
    itemModalOverlay.dataset.activeItemId = String(itemId);
    itemModalOverlay.classList.add('show-modal');
    document.body.style.overflow = 'hidden';
    console.log('Modal should now be visible');
}

function hideModal() {
    console.log('hideModal called');
    itemModalOverlay.classList.remove('show-modal');
    delete itemModalOverlay.dataset.activeItemId;
    document.body.style.overflow = '';
}

// Attach event listeners to modal close button
if (modalCloseBtn) {
    modalCloseBtn.onclick = hideModal;
    console.log('Close button listener attached');
}

// Close modal when clicking outside the modal content
if (itemModalOverlay) {
    itemModalOverlay.onclick = (e) => {
        if (e.target === itemModalOverlay) {
            hideModal();
        }
    };
    console.log('Overlay listener attached');
}

// Attach click listeners to all info icons
function attachModalListeners() {
    const infoIcons = document.querySelectorAll('.info-icon');
    console.log('Found info icons:', infoIcons.length);

    infoIcons.forEach((icon, index) => {
        console.log(`Attaching listener to icon ${index}, itemId:`, icon.dataset.itemId);
        icon.onclick = (e) => {
            e.stopPropagation();
            const itemId = icon.dataset.itemId;
            console.log('Info icon clicked, itemId:', itemId);
            showModal(itemId);
        };
    });
}