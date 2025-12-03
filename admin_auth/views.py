from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import AdminUser

def admin_login(request):
    """
    Handles admin login functionality.
    - Accepts admin credentials via POST request.
    - Validates the credentials against stored admin data.
    - If valid, creates a session and redirects to the admin dashboard (pending orders page).
    - If invalid, displays an appropriate error message.
    """
    if request.method == "POST":
        # Retrieve admin credentials from the submitted login form
        admin_id = request.POST.get("adminid")
        password = request.POST.get("password")

        try:
            # Check if an admin user with the provided admin_id exists
            user = AdminUser.objects.get(admin_id=admin_id)
            if check_password(password, user.password):
                 # Store admin ID in session to maintain logged-in state
                request.session['admin_id'] = user.admin_id

                # Redirect to the pending orders page after successful login
                return redirect("pending_table_orders")
            else:
                # Display an error message if the password is incorrect
                messages.error(request, "Invalid Admin ID or Password")
        except AdminUser.DoesNotExist:
            # Display an error message if the admin ID does not exist in the database
            messages.error(request, "Invalid Admin ID or Password")
    
    # Render the login page (GET request or failed login attempt)
    return render(request, "login.html")