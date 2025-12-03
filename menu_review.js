// --- MODAL & DATA ---
const itemModalOverlay = document.getElementById("itemModalOverlay");
const itemModalBody = document.querySelector(".modal-body");
const modalCloseBtn = document.getElementById("modalCloseBtn");

// Menu Data: Expanded to all 16 categories (using dummy data for new categories)
const menuData = {
    // --- COCKTAILS ---
    "The Aperol Affair": {
        category: "Cocktails",
        price: "Php 450.00",
        description: "A bright and zesty blend of Aperol, sparkling wine, and a splash of soda, perfect for a sunny evening.",
        iconSrc: "cocktail.png",
    },
    "Cucumber Smash": {
        category: "Cocktails",
        price: "Php 480.00",
        description: "A refreshing muddle of cucumber, mint, gin, and lime. Cool and herbaceous.",
        iconSrc: "cocktail.png",
    },

    // --- SHOOTERS ---
    "Jager Bomb": {
        category: "Shooters",
        price: "Php 300.00",
        description: "A shot of Jägermeister dropped into an energy drink.",
        iconSrc: "shooter.png",
    },
    
    // --- SINGLE SHOTS ---
    "Tequila Gold Shot": {
        category: "Single Shots",
        price: "Php 250.00",
        description: "A single shot of premium gold tequila.",
        iconSrc: "shot.png",
    },

    // --- MOCKTAILS ---
    "Virgin Mojito": {
        category: "Mocktails",
        price: "Php 280.00",
        description: "Refreshing mix of lime, mint, simple syrup, and soda water.",
        iconSrc: "cocktail.png",
    },

    // --- FRUITS ---
    "Watermelon Shake": {
        category: "Fruits",
        price: "Php 180.00",
        description: "Freshly blended watermelon with crushed ice.",
        iconSrc: "fruit.png",
    },

    // --- BEERS ---
    "San Miguel Pale Pilsen": {
        category: "Beers",
        price: "Php 120.00",
        description: "The classic Filipino pale lager. Crisp and refreshing.",
        iconSrc: "cocktail.png",
    },

    // --- BEVERAGES ---
    "Coke Zero": {
        category: "Beverages",
        price: "Php 90.00",
        description: "A bottle of cold Coca-Cola Zero.",
        iconSrc: "soda.png",
    },

    // --- FOOD ---
    "Cheesy Nachos": {
        category: "Food",
        price: "Php 550.00",
        description: "Tortilla chips loaded with ground beef, cheese sauce, jalapeños, and sour cream.",
        iconSrc: "restaurant.png",
    },
    
    // --- RUM ---
    "Bacardi Gold (Bottle)": {
        category: "Rum",
        price: "Php 2,500.00",
        description: "A full bottle of Bacardi Gold rum.",
        iconSrc: "rum.png",
    },

    // --- TEQUILLA ---
    "Patrón Añejo (Shot)": {
        category: "Tequilla",
        price: "Php 600.00",
        description: "Premium aged Tequila shot.",
        iconSrc: "tequila.png",
    },

    // --- VODKA ---
    "Absolut Blue (Shot)": {
        category: "Vodka",
        price: "Php 350.00",
        description: "A clean and crisp shot of Absolut Vodka.",
        iconSrc: "vodka.png",
    },

    // --- GIN ---
    "Bombay Sapphire (Bottle)": {
        category: "Gin",
        price: "Php 3,200.00",
        description: "A full bottle of London Dry Gin.",
        iconSrc: "gin.png",
    },

    // --- WINE ---
    "Merlot Reserve": {
        category: "Wine",
        price: "Php 1,200.00",
        description: "A smooth, full-bodied red wine with notes of black cherry and plum.",
        iconSrc: "gin.png",
    },

    // --- WHISKY/SCOTCH ---
    "Johnnie Walker Black Label (Shot)": {
        category: "Whisky/Scotch",
        price: "Php 450.00",
        description: "A smooth, smoky blended Scotch whisky.",
        iconSrc: "vodka.png",
    },

    // --- BRANDY/COGNAC ---
    "Hennessy VSOP (Shot)": {
        category: "Brandy/Cognac",
        price: "Php 700.00",
        description: "A rich and complex Cognac shot.",
        iconSrc: "rum.png",
    },

    // --- LIQUERS ---
    "Baileys Irish Cream (Shot)": {
        category: "Liquers",
        price: "Php 380.00",
        description: "Sweet, creamy liqueur with a hint of cocoa and vanilla.",
        iconSrc: "rum.png",
    },
};

// --- DROPDOWN TOGGLE LOGIC (Generalized) ---

// Define all 16 categories for automated setup
const categories = [
    "Cocktails", "Shooters", "Single Shots", "Mocktails", "Fruits", "Beers", 
    "Beverages", "Food", "Rum", "Tequilla", "Vodka", "Gin", "Wine", 
    "Whisky/Scotch", "Brandy/Cognac", "Liquers"
];

// Helper to sanitize category name for HTML ID (e.g., 'Whisky/Scotch' -> 'whiskyscotch')
function sanitizeId(category) {
    return category.toLowerCase().replace(/[^a-z0-9]/g, '');
}

// Function to handle the toggle with sliding animation
function setupDropdownToggle(category) {
    const id = sanitizeId(category);
    const toggle = document.getElementById(id + "Toggle");
    const content = document.getElementById(id + "Dropdown");
    const arrow = toggle.querySelector(".dropdown-arrow"); // Get the arrow element

    if (toggle && content) {
        // 1. INITIALIZE (For "Default Show All" state)
        // We set the max-height to a large value (like its scrollHeight) 
        // to ensure it is visible and can contract properly on the first click.
        // We run this AFTER the DOM is rendered (later in the script).
        
        // Function to set the dropdown height
        function toggleDropdown() {
            // Determine if the content is currently visible
            const isVisible = content.style.maxHeight && content.style.maxHeight !== "0px";

            if (isVisible) {
                // If visible, collapse it (Slide Up)
                content.style.maxHeight = "0px";
                arrow.classList.remove("bi-caret-up-fill");
                arrow.classList.add("bi-caret-down-fill");
            } else {
                // If collapsed, expand it (Slide Down)
                // Set to the actual full height (scrollHeight) to enable the slide transition
                content.style.maxHeight = content.scrollHeight + "px";
                arrow.classList.remove("bi-caret-down-fill");
                arrow.classList.add("bi-caret-up-fill");
            }
        }
        
        toggle.addEventListener("click", toggleDropdown);

        // Optional: Ensure the dropdown is set to its initial full height after load
        // We run this function outside the loop for the current element:
        function setInitialHeight() {
            // Only set height if the element is present, to ensure "Default Show All"
            if (content) {
                // Set max-height to its full content size
                content.style.maxHeight = content.scrollHeight + "px";
                // Change arrow direction to 'up' to show it's open
                arrow.classList.remove("bi-caret-down-fill");
                arrow.classList.add("bi-caret-up-fill");
            }
        }
        // Run the setup after a short delay to ensure content has rendered
        setTimeout(setInitialHeight, 10);
    }
}

// Setup all dropdowns on load
categories.forEach(setupDropdownToggle);


// Order Logic (unchanged, but now handles all items in menuData)
const summaryList = document.getElementById("summaryList");
let order = {};

function changeQuantity(itemName, delta) {
    const itemCards = document.querySelectorAll(`.item-card[data-item="${itemName}"]`);
    
    let currentQty = order[itemName] || 0;
    let newQty = Math.max(0, currentQty + delta);

    if (newQty > 0) order[itemName] = newQty;
    else delete order[itemName];

    itemCards.forEach(card => {
        card.querySelector(".qty").textContent = newQty;
    });

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

// Menu Card Quantity Controls (Must be run after all HTML is loaded)
function attachMenuListeners() {
    document.querySelectorAll(".item-card .plus").forEach((btn) => {
        btn.onclick = () => {
            const itemName = btn.closest(".item-card").dataset.item;
            changeQuantity(itemName, 1);
        };
    });

    document.querySelectorAll(".item-card .minus").forEach((btn) => {
        btn.onclick = () => {
            const itemName = btn.closest(".item-card").dataset.item;
            changeQuantity(itemName, -1);
        };
    });
}

// Attach listeners on load
attachMenuListeners();


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
