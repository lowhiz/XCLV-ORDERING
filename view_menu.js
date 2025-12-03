document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Info Icon Modal Functionality ---

    // Get the new modal elements
    const modal = document.getElementById('itemDetailsModal');
    const modalTitle = document.getElementById('modalItemName');
    const modalCategory = document.getElementById('modalCategory');
    const modalPrice = document.getElementById('modalPrice');
    const modalDescription = document.getElementById('modalDescription');
    const closeBtn = document.querySelector('.modal-close-btn');
    const infoButtons = document.querySelectorAll('.info-icon-btn');

    // Function to show the modal with full details
    function openModal(itemName, itemCategory, itemPrice, itemDescription) {
        modalTitle.textContent = itemName;
        modalCategory.textContent = itemCategory;
        modalPrice.textContent = itemPrice;
        modalDescription.textContent = itemDescription;
        
        modal.style.display = 'flex'; // Use 'flex' to center content
    }

    // Function to hide the modal
    function closeModal() {
        modal.style.display = 'none';
    }

    // Event listener for Info Icons
    infoButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            // Stop propagation to prevent any potential click event on the parent card
            event.stopPropagation(); 
            
            // Retrieve all data attributes
            const itemName = button.dataset.itemName;
            const itemCategory = button.dataset.itemCategory || 'N/A';
            const itemPrice = button.dataset.itemPrice || '0.00';
            const itemDescription = button.dataset.itemDesc || 'No description available.';

            openModal(itemName, itemCategory, itemPrice, itemDescription);
        });
    });

    // Event listener for the close button
    closeBtn.addEventListener('click', closeModal);

    // Close modal when clicking outside of the modal content
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Close modal on escape key press
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal.style.display === 'flex') {
            closeModal();
        }
    });

    // --- 2. Quantity Controls Functionality ---

    const menuItems = document.querySelectorAll('.menu-item-card');

    menuItems.forEach(card => {
        const minusBtn = card.querySelector('.qty-minus');
        const plusBtn = card.querySelector('.qty-plus');
        const qtyDisplay = card.querySelector('.qty-display');
        
        // Use the initial quantity set in the HTML for design consistency (e.g., 99)
        let quantity = parseInt(qtyDisplay.textContent); 

        // Plus button handler
        plusBtn.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent card click event if any
            quantity++;
            qtyDisplay.textContent = quantity;
            qtyDisplay.dataset.currentQty = quantity;
            console.log(`Increased ${card.dataset.itemId} to ${quantity}`);
        });

        // Minus button handler
        minusBtn.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent card click event if any
            if (quantity > 0) {
                quantity--;
                qtyDisplay.textContent = quantity;
                qtyDisplay.dataset.currentQty = quantity;
                console.log(`Decreased ${card.dataset.itemId} to ${quantity}`);
            }
        });
    });
});