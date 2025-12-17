// Initialize cart with current order quantities
let cart = {};

// Load current quantities from the template
document.addEventListener('DOMContentLoaded', function() {
    const editOrderData = document.getElementById('edit-order-data');
    const tableOrderId = editOrderData.dataset.tableOrderId;
    const currentQuantities = editOrderData.dataset.currentQuantities;

    console.log('Loading current quantities:', currentQuantities); // Debug line

    // Parse current quantities and populate cart
    try {
        // Handle case where currentQuantities might be empty or malformed
        if (currentQuantities && currentQuantities !== '{}' && currentQuantities !== 'None') {
            const quantities = JSON.parse(currentQuantities.replace(/'/g, '"'));
            console.log('Parsed quantities:', quantities); // Debug line

            for (const [itemId, quantity] of Object.entries(quantities)) {
                if (quantity > 0) {
                    // Find the item details from the page
                    const quantityElement = document.getElementById(`quantity-${itemId}`);
                    if (quantityElement) {
                        const menuItem = quantityElement.closest('.menu-item');
                        // FIX: match the template's col-8 container
                        const itemName = menuItem.querySelector('.col-8 span').textContent.trim();
                        const priceText = menuItem.querySelector('.text-muted').textContent;
                        const itemPrice = parseFloat(priceText.replace('Php ', '').replace(',', ''));

                        cart[itemId] = {
                            id: itemId,
                            name: itemName,
                            price: itemPrice,
                            quantity: parseInt(quantity)
                        };

                        console.log(`Added to cart: ${itemName} x${quantity}`); // Debug line
                    }
                }
            }
        }

        // Also initialize cart from the displayed quantities on the page
        const quantityElements = document.querySelectorAll('[id^="quantity-"]');
        quantityElements.forEach(element => {
            const itemId = element.id.replace('quantity-', '');
            const displayedQuantity = parseInt(element.textContent) || 0;

            if (displayedQuantity > 0 && !cart[itemId]) {
                const menuItem = element.closest('.menu-item');
                // FIX: match the template's col-8 container
                const itemName = menuItem.querySelector('.col-8 span').textContent.trim();
                const priceText = menuItem.querySelector('.text-muted').textContent;
                const itemPrice = parseFloat(priceText.replace('Php ', '').replace(',', ''));

                cart[itemId] = {
                    id: itemId,
                    name: itemName,
                    price: itemPrice,
                    quantity: displayedQuantity
                };

                console.log(`Backup init: ${itemName} x${displayedQuantity}`); // Debug line
            }
        });

    } catch (e) {
        console.error('Error parsing current quantities:', e);

        // Fallback: Initialize from displayed quantities
        const quantityElements = document.querySelectorAll('[id^="quantity-"]');
        quantityElements.forEach(element => {
            const itemId = element.id.replace('quantity-', '');
            const displayedQuantity = parseInt(element.textContent) || 0;

            if (displayedQuantity > 0) {
                const menuItem = element.closest('.menu-item');
                // FIX: match the template's col-8 container
                const itemName = menuItem.querySelector('.col-8 span').textContent.trim();
                const priceText = menuItem.querySelector('.text-muted').textContent;
                const itemPrice = parseFloat(priceText.replace('Php ', '').replace(',', ''));

                cart[itemId] = {
                    id: itemId,
                    name: itemName,
                    price: itemPrice,
                    quantity: displayedQuantity
                };
            }
        });
    }

    console.log('=== INITIALIZATION COMPLETE ===');
    console.log('Final cart state:', cart);
    console.log('Total items in cart:', Object.keys(cart).length);
    console.log('Items:', Object.values(cart).map(item => `${item.name} x${item.quantity}`));
    console.log('================================');
    updateOrderSummary();
});

function increaseQuantity(itemId, itemName, itemPrice) {
    console.log(`Increase: ${itemId}, ${itemName}, ${itemPrice}`); // Debug line

    if (!cart[itemId]) {
        // Initialize from currently displayed quantity instead of starting at 0
        const quantityElement = document.getElementById(`quantity-${itemId}`);
        const currentDisplayed = quantityElement ? parseInt(quantityElement.textContent) || 0 : 0;

        cart[itemId] = {
            id: itemId,
            name: itemName,
            price: parseFloat(itemPrice),
            quantity: currentDisplayed
        };
    }

    if (cart[itemId].quantity < 99) {
        cart[itemId].quantity++;
        updateDisplay(itemId);
        updateOrderSummary();
    }

    console.log('Cart after increase:', cart[itemId]); // Debug line
    console.log('Full cart now:', Object.keys(cart)); // Debug line
}

function decreaseQuantity(itemId) {
    console.log(`Decrease attempt: ${itemId}`, cart[itemId]); // Debug line

    // Check if item exists in cart
    if (!cart[itemId]) {
        // If not in cart, initialize it from the displayed quantity
        const quantityElement = document.getElementById(`quantity-${itemId}`);
        if (quantityElement) {
            const currentDisplayed = parseInt(quantityElement.textContent) || 0;
            if (currentDisplayed > 0) {
                const menuItem = quantityElement.closest('.menu-item');
                // FIX: match the template's col-8 container
                const itemName = menuItem.querySelector('.col-8 span').textContent.trim();
                const priceText = menuItem.querySelector('.text-muted').textContent;
                const itemPrice = parseFloat(priceText.replace('Php ', '').replace(',', ''));

                cart[itemId] = {
                    id: itemId,
                    name: itemName,
                    price: itemPrice,
                    quantity: currentDisplayed
                };

                console.log(`Initialized cart for decrease: ${itemName} x${currentDisplayed}`); // Debug line
            }
        }
    }

    // Now try to decrease
    if (cart[itemId] && cart[itemId].quantity > 0) {
        cart[itemId].quantity--;
        console.log(`Decreased to: ${cart[itemId].quantity}`); // Debug line

        if (cart[itemId].quantity === 0) {
            delete cart[itemId];
            console.log(`Removed item ${itemId} from cart`); // Debug line
        }
        updateDisplay(itemId);
        updateOrderSummary();
    } else {
        console.log(`Cannot decrease ${itemId}: not in cart or quantity is 0`); // Debug line
    }
}

function updateDisplay(itemId) {
    const quantityElement = document.getElementById(`quantity-${itemId}`);
    const quantity = cart[itemId] ? cart[itemId].quantity : 0;
    quantityElement.textContent = quantity;

    // Update item styling
    const menuItem = quantityElement.closest('.menu-item');
    if (quantity > 0) {
        menuItem.classList.add('current-item');
    } else {
        menuItem.classList.remove('current-item');
    }

    console.log(`Updated display for ${itemId}: ${quantity}`); // Debug line
}

function updateOrderSummary() {
    // Update the order total display
    let total = 0;

    for (const item of Object.values(cart)) {
        if (item.quantity > 0) {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;
        }
    }

    // Find and update the total in the fixed bottom section
    const totalElement = document.querySelector('.fixed-bottom-section h3 strong');
    if (totalElement) {
        totalElement.textContent = `Php ${total.toFixed(2)}`;
    }

    console.log('Order summary updated. Total:', total); // Debug line
}

function saveOrderChanges() {
    const editOrderData = document.getElementById('edit-order-data');
    const tableOrderId = editOrderData.dataset.tableOrderId;

    // Prepare order items
    const orderItems = Object.values(cart).filter(item => item.quantity > 0);

    console.log('=== SAVE ORDER DEBUG ===');
    console.log('Full cart object:', cart);
    console.log('Cart keys:', Object.keys(cart));
    console.log('Order items to save:', orderItems);
    console.log('Number of items:', orderItems.length);
    console.log('========================');

    if (confirm('Are you sure you want to save these changes to the order?')) {
        // Send updated order to server
        fetch('/orders/update-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                table_order_id: tableOrderId,
                items: orderItems
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Order updated successfully!');
                window.location.href = '/tables/?admin=true';
            } else {
                alert('Error updating order: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the order');
        });
    }
}

function cancelEdit() {
  window.location.href = '/tables/?admin=true';
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
