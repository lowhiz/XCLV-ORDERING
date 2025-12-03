let orderData = null;

// Load order data on page load
document.addEventListener("DOMContentLoaded", function () {
  loadOrderData();
});

function loadOrderData() {
  const savedData = sessionStorage.getItem("orderData");

  if (!savedData) {
    showEmptyOrder();
    return;
  }

  try {
    orderData = JSON.parse(savedData);
    displayOrderItems();
  } catch (error) {
    console.error("Error loading order data:", error);
    showEmptyOrder();
  }
}

function showEmptyOrder() {
  document.getElementById("review-items").innerHTML = `
              <div class="empty-order">
                  <h3>No items in your order</h3>
                  <p>Please go back to the menu and add items to your order.</p>
              </div>
          `;
  const confirmBtn = document.getElementById("confirm-btn");
  confirmBtn.disabled = true;
  confirmBtn.style.background = "#ccc";
}

function displayOrderItems() {
  const reviewContainer = document.getElementById("review-items");
  const grandTotalElement = document.getElementById("grand-total");

  if (!orderData || !orderData.items || orderData.items.length === 0) {
    showEmptyOrder();
    return;
  }

  let itemsHtml = "";
  let grandTotal = 0;

  orderData.items.forEach((item) => {
    const itemTotal = item.price * item.quantity;
    grandTotal += itemTotal;

    itemsHtml += `
                  <div class="order-item">
                      <div class="item-details">
                          <div class="item-name">${item.name}</div>
                          <div class="item-price">₱${item.price.toFixed(2)} each</div>
                      </div>
                      <div class="item-quantity">×${item.quantity}</div>
                      <div class="item-total">₱${itemTotal.toFixed(2)}</div>
                  </div>
              `;
  });

  reviewContainer.innerHTML = itemsHtml;
  grandTotalElement.textContent = `Total: ₱${grandTotal.toFixed(2)}`;
}

function confirmOrder() {
  if (!orderData || !orderData.items || orderData.items.length === 0) {
    alert("No items to order!");
    return;
  }

  // Debugging: echo all items in the console before sending
  console.log("DEBUG: Items about to be sent to server:");
  orderData.items.forEach((item, index) => {
    console.log(`Item ${index + 1}: ID=${item.id}, Name=${item.name}, Quantity=${item.quantity}, Price=${item.price}`);
  });

  // Disable button to prevent double-clicking
  const confirmBtn = document.getElementById("confirm-btn");
  confirmBtn.disabled = true;
  confirmBtn.textContent = "Processing...";

  const menuData = document.getElementById("menu-data");
  const tableId = menuData.dataset.tableId;
  fetch("/orders/order/", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
      },
      body: JSON.stringify({
          items: orderData.items,
          table_id: tableId,
      }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Instead of alert, redirect to success page
        if (data.redirect_url) {
          window.location.href = data.redirect_url;
        }

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

}
