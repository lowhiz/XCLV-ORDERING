// JavaScript to update time and date
function updatePhilippineTime() {
  const optionsTime = { hour: "2-digit", minute: "2-digit", hour12: true };
  const optionsDate = { day: "2-digit", month: "short", year: "numeric" };

  // Get Philippine time zone
  const now = new Date().toLocaleString("en-US", { timeZone: "Asia/Manila" });
  const phDate = new Date(now);

  // Format
  const timeStr = phDate.toLocaleTimeString("en-US", optionsTime).toUpperCase();
  const dateStr = phDate
    .toLocaleDateString("en-US", optionsDate)
    .toUpperCase()
    .replace(",", "");

  document.getElementById("ph-time").textContent = timeStr;
  document.getElementById("ph-date").textContent = dateStr;
}

// Update every second
setInterval(updatePhilippineTime, 1000);
updatePhilippineTime();
