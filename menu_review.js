// --- MODAL & DATA ---
const itemModalOverlay = document.getElementById("itemModalOverlay");
const itemModalBody = document.querySelector(".modal-body");
const modalCloseBtn = document.getElementById("modalCloseBtn");

// Menu Data
const menuData = {
  "The Aperol Affair": {
    category: "Cocktails",
    price: "Php 450.00",
    description:
      "A bright and zesty blend of Aperol, sparkling wine, and a splash of soda, perfect for a sunny evening.",
    iconSrc: "cocktail.png",
  },
  "Cucumber Smash": {
    category: "Cocktails",
    price: "Php 480.00",
    description:
      "A refreshing muddle of cucumber, mint, gin, and lime. Cool and herbaceous.",
    iconSrc: "cocktail.png",
  },
};

// Dropdown Toggle
const toggle = document.getElementById("cocktailToggle");
const content = document.getElementById("cocktailDropdown");
toggle.addEventListener("click", () => {
  content.classList.toggle("show");
});

// Order Logic
const summaryList = document.getElementById("summaryList");
let order = {};

function changeQuantity(itemName, delta) {
  const card = document.querySelector(`.item-card[data-item="${itemName}"]`);
  let currentQty = order[itemName] || 0;
  let newQty = Math.max(0, currentQty + delta);

  if (newQty > 0) order[itemName] = newQty;
  else delete order[itemName];

  if (card) card.querySelector(".qty").textContent = newQty;

  updateSummary();
}

function updateSummary() {
  summaryList.innerHTML = "";

  for (const itemName in order) {
    const qty = order[itemName];
    const itemIcon = menuData[itemName]?.iconSrc || "cocktail.png";

    let li = document.createElement("li");
    li.className = "summary-item-card";
    li.dataset.item = itemName;

    li.innerHTML = `
      <div class="left">
        <img src="${itemIcon}" class="drink-icon" />
        <i class="bi bi-info-circle info-icon" data-item="${itemName}"></i>
        <p class="drink-title">${itemName}</p>
      </div>
      <div class="right">
        <button class="qty-btn minus" data-item="${itemName}">−</button>
        <span class="qty summary-qty">${qty}</span>
        <button class="qty-btn plus" data-item="${itemName}">+</button>
      </div>
    `;

    summaryList.appendChild(li);
  }

  attachSummaryListeners();
  attachModalListeners();
}

// Summary Quantity Controls
function attachSummaryListeners() {
  document.querySelectorAll(".summary-item-card .plus").forEach((btn) => {
    btn.onclick = () => changeQuantity(btn.dataset.item, 1);
  });

  document.querySelectorAll(".summary-item-card .minus").forEach((btn) => {
    btn.onclick = () => changeQuantity(btn.dataset.item, -1);
  });
}

// Menu Card Quantity Controls
const menuPlusButtons = document.querySelectorAll(".item-card .plus");
const menuMinusButtons = document.querySelectorAll(".item-card .minus");

menuPlusButtons.forEach((btn) => {
  btn.onclick = () => {
    const itemName = btn.closest(".item-card").dataset.item;
    changeQuantity(itemName, 1);
  };
});

menuMinusButtons.forEach((btn) => {
  btn.onclick = () => {
    const itemName = btn.closest(".item-card").dataset.item;
    changeQuantity(itemName, -1);
  };
});

// --- MODAL ---
function showModal(itemName) {
  const data = menuData[itemName];
  if (!data) return;

  itemModalBody.innerHTML = `
    <div class="modal-info-card">
      <div class="modal-item-header">
        <img src="${data.iconSrc}" class="drink-icon modal-icon" />
        <div class="modal-text-group">
          <p class="modal-item-title">${itemName}</p>
          <p class="modal-category">Category: ${data.category}</p>
          <p class="modal-price">${data.price}</p>
        </div>
      </div>
      <div class="modal-description-section">
        <p class="modal-description-label">Description:</p>
        <p class="modal-description-text">${data.description}</p>
      </div>
    </div>
  `;

  itemModalOverlay.classList.add("show-modal");
  document.body.style.overflow = "hidden";
}

function hideModal() {
  itemModalOverlay.classList.remove("show-modal");
  document.body.style.overflow = "";
}

modalCloseBtn.onclick = hideModal;
itemModalOverlay.onclick = (e) => {
  if (e.target === itemModalOverlay) hideModal();
};

// Attach listeners to info icons
function attachModalListeners() {
  document.querySelectorAll(".info-icon").forEach((icon) => {
    const itemName = icon.dataset.item;

    const handler = (e) => {
      e.stopPropagation();
      showModal(itemName);
    };

    icon.onclick = handler;
  });
}

attachModalListeners();
