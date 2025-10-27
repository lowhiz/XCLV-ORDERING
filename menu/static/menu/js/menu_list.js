let cart = {}; // Track quantities by item ID

function increaseQuantity(itemId, itemName, itemPrice) {
  // Initialize if doesn't exist
  if (!cart[itemId]) {
    cart[itemId] = {
      id: itemId,
      name: itemName,
      price: parseFloat(itemPrice),
      quantity: 0,
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
  const orderTotalElement = document.getElementById("order-total");

  // Clear current order summary
  orderItemsContainer.innerHTML = "";

  const cartItems = Object.values(cart).filter((item) => item.quantity > 0);

  if (cartItems.length === 0) {
    orderItemsContainer.innerHTML = "<p>No items ordered yet.</p>";
    orderTotalElement.textContent = "Total: ₱0.00";
    return;
  }

  // Create order summary items
  cartItems.forEach((item) => {
    const orderItem = document.createElement("div");
    orderItem.className = "order-item";
    orderItem.innerHTML = `
                    <table>
                        <tr>
                            <td>${item.name}</td>
                            <td>
                                <button onclick="decreaseQuantity('${item.id}')">-</button>
                                <span style="margin: 0 10px; font-weight: bold;">${item.quantity}</span>
                                <button onclick="increaseQuantity('${item.id}', '${item.name}', ${item.price})">+</button>
                            </td>
                            <td>₱${(item.price * item.quantity).toFixed(2)}</td>
                        </tr>
                    </table>
                `;
    orderItemsContainer.appendChild(orderItem);
  });

  // Calculate and display total
  const total = cartItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0,
  );
  orderTotalElement.textContent = `Total: ₱${total.toFixed(2)}`;
}

function updateCartDisplay() {
  const cartElement = document.getElementById("cart");
  const cartCount = document.getElementById("cart-count");

  const totalItems = Object.values(cart).reduce(
    (sum, item) => sum + item.quantity,
    0,
  );

  if (totalItems > 0) {
    cartElement.style.display = "block";
    cartCount.textContent = totalItems;
  } else {
    cartElement.style.display = "none";
  }
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
  sessionStorage.setItem(
    "orderData",
    JSON.stringify({
      items: orderItems,
      table_id: "{{ table_id }}",
      table_display: "{{ table_display }}",
    }),
  );

  // Redirect to review page
  window.location.href = "/menu/review/";
}

// Initialize order summary on page load
document.addEventListener("DOMContentLoaded", function () {
  updateOrderSummary();
});
