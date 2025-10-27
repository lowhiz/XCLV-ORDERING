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
  document.getElementById("confirm-btn").disabled = true;
  document.getElementById("confirm-btn").style.background = "#ccc";
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

  // Disable button to prevent double-clicking
  const confirmBtn = document.getElementById("confirm-btn");
  confirmBtn.disabled = true;
  confirmBtn.textContent = "Processing...";

  fetch("/menu/order/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}",
    },
    body: JSON.stringify({
      items: orderData.items,
      table_id: orderData.table_id,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Order placed successfully!");

        // Clear order data
        sessionStorage.removeItem("orderData");

        // Redirect back to menu
        window.location.href = "/menu/";
      } else {
        alert("Error placing order: " + data.error);

        // Re-enable button
        confirmBtn.disabled = false;
        confirmBtn.textContent = "Confirm Order";
      }
    })
    .catch((error) => {
      alert("Network error. Please try again.");

      // Re-enable button
      confirmBtn.disabled = false;
      confirmBtn.textContent = "Confirm Order";
    });
}
