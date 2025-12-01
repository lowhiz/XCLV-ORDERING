let updateInterval;

function updateTableStatuses() {
  console.log("Updating table statuses...");

  fetch(window.TABLE_STATUS_API_URL)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Received data:", data);

      let activeTablesCount = 0;

      // Reset all tables to their original classes first
      document.querySelectorAll(".table-div").forEach((tableDiv) => {
        tableDiv.classList.remove(
          "table-status-available",
          "table-status-pending",
        );
      });

      // Update each table based on status
      Object.keys(data).forEach((tableKey) => {
        const tableStatus = data[tableKey];
        const tableDiv = document.querySelector(`[data-table="${tableKey}"]`);

        console.log(`Processing table: ${tableKey}, status:`, tableStatus);

        if (tableDiv) {
          activeTablesCount++;

          if (tableStatus.has_pending_orders) {
            tableDiv.classList.add("table-status-pending");
            console.log(`Added pending class to ${tableKey}`);
          } else {
            tableDiv.classList.add("table-status-available");
            console.log(`Added available class to ${tableKey}`);
          }
        } else {
          console.warn(`Table div not found for: ${tableKey}`);
        }
      });

      // Update active tables count
      const countElement = document.getElementById("active-tables-count");
      if (countElement) {
        countElement.textContent = activeTablesCount;
      }

      console.log(`Updated ${activeTablesCount} tables`);
    })
    .catch((error) => {
      console.error("Error fetching table status:", error);
      const countElement = document.getElementById("active-tables-count");
      if (countElement) {
        countElement.textContent = "Error";
      }
    });
}

// Initialize the page
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM loaded, initializing table status updates...");

  // Update immediately on page load
  updateTableStatuses();

  // Set up automatic updates every 5 seconds
  updateInterval = setInterval(updateTableStatuses, 5000);
});

// Clean up interval when page is hidden/unloaded
document.addEventListener("visibilitychange", function () {
  if (document.hidden) {
    clearInterval(updateInterval);
    console.log("Page hidden, stopping updates");
  } else {
    updateInterval = setInterval(updateTableStatuses, 5000);
    updateTableStatuses(); // Update immediately when page becomes visible
    console.log("Page visible, resuming updates");
  }
});
