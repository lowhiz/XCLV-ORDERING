let updateInterval;

function renderPendingOrders(orders) {
  const scrollableSection = document.querySelector('.scrollable-orders-section');

  if (!scrollableSection) {
    console.error('Scrollable section not found');
    return;
  }

  // If no orders, show empty state
  if (orders.length === 0) {
    scrollableSection.innerHTML = `
      <div class="empty-state d-flex flex-column justify-content-center align-items-center pt-5" style="min-height: calc(100vh - 200px);">
        <img src="/static/images/pending.svg" alt="Inactive Table" class="mb-3" style="max-width: 100px; opacity: 35%;">
        <h2 class="text-center">No pending orders currently in queue</h2>
        <p class="text-center">Customers and their orders after filling up in the menu <br> are showed on this page.</p>
      </div>
    `;
    return;
  }

  // Build the orders HTML
  let ordersHTML = '';

  orders.forEach(order => {
    // Build items list
    let itemsHTML = '';
    order.items.forEach(item => {
      itemsHTML += `<p class="item-name">x${item.quantity} ${item.name}</p>`;
    });

    // Build the order card
    ordersHTML += `
      <div class="order-item">
        <div class="order-details">
          <div class="table-id-time">
            <span class="table-id montserrat">${order.description}</span>
            <span class="order-time fs-4">${order.order_time}</span>
          </div>
          <div class="order-items">
            ${itemsHTML}
          </div>
        </div>
        <div class="order-actions">
          <a href="/tables/edit-order/${order.table_order_id}/" class="action-btn edit-btn">
            <img src="/static/images/edit.svg" alt="Edit" class="action-icon" />
          </a>
          <a href="/tables/delete-order/${order.table_order_id}/" class="action-btn reject-btn">
            <img src="/static/images/x.svg" alt="Reject" class="action-icon" />
          </a>
          <a href="/tables/complete-order/${order.table_order_id}/" class="action-btn accept-btn">
            <img src="/static/images/check.svg" alt="Accept" class="action-icon" />
          </a>
        </div>
      </div>
    `;
  });

  // Update the scrollable section with order list
  scrollableSection.innerHTML = `<div class="order-list">${ordersHTML}</div>`;
}

function updatePendingOrders() {
  console.log('Fetching pending orders...');

  fetch(window.PENDING_ORDERS_API_URL)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Received pending orders:', data);
      renderPendingOrders(data);
    })
    .catch(error => {
      console.error('Error fetching pending orders:', error);
    });
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing pending orders updates...');

  // Check if we're on the pending orders page
  const scrollableSection = document.querySelector('.scrollable-orders-section');
  if (!scrollableSection) {
    console.log('Not on pending orders page, skipping initialization');
    return;
  }

  // Update immediately on page load
  updatePendingOrders();

  // Set up automatic updates every 5 seconds
  updateInterval = setInterval(updatePendingOrders, 5000);
});

// Clean up interval when page is hidden/unloaded
document.addEventListener('visibilitychange', function() {
  if (document.hidden) {
    clearInterval(updateInterval);
    console.log('Page hidden, stopping updates');
  } else {
    updateInterval = setInterval(updatePendingOrders, 5000);
    updatePendingOrders(); // Update immediately when page becomes visible
    console.log('Page visible, resuming updates');
  }
});

// Optional: Play sound notification when new orders arrive
let previousOrderCount = 0;

function checkForNewOrders(orders) {
  if (previousOrderCount > 0 && orders.length > previousOrderCount) {
    console.log('New order detected!');
    // You can add a sound notification here if desired
    // new Audio('/static/sounds/notification.mp3').play();
  }
  previousOrderCount = orders.length;
}
