document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const errorMessage = document.getElementById('errorMessage');
    
    // Check if the form and error message elements exist
    if (!form || !errorMessage) {
        console.error("Form or Error Message element not found.");
        return;
    }

    form.addEventListener('submit', function(event) {
        // Prevent the default form submission (page reload)
        event.preventDefault(); 

        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');

        // Check if input elements exist
        if (!usernameInput || !passwordInput) {
            console.error("Username or Password input field not found.");
            return;
        }

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // --- Simple client-side validation for demonstration ---
        // Replace this with your actual API call/server-side check
        if (username === 'admin' && password === 'admin123') {
            // Success: Hide the error message
            errorMessage.classList.add('d-none');
            alert('Login successful! Redirecting to dashboard...');
            // In a real application, you would use window.location.href = 'dashboard.html';
        } else {
            // Failure: Show the error message
            errorMessage.classList.remove('d-none');
        }
    });
});