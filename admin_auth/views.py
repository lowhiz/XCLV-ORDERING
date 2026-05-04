from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from functools import wraps
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
    return render(request, "admin_auth.html")

def admin_required(view_func):
    """
    Decorator to ensure only logged-in admins can access certain views.
    """
    @wraps(view_func)

    # OLD LOGIN MECHANISM: Checks for 'admin_id' in session to verify
    # if the user is logged in as admin.

    # def wrapper(request, *args, **kwargs):
    #     if 'admin_id' not in request.session:
    #         messages.error(request, "Please log in to access this page.")
    #         return redirect('admin_login')
    #     return view_func(request, *args, **kwargs)
    # return wrapper

    # NEW LOGIN MECHANISM: Uses OAuth2 for Django to manage the session
    # through request.user. Checks request.user.is_authenticated instead

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please sign in to access this page.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_logout(request):
    """
    Handles admin logout functionality.
    - Clears the admin session.
    - Redirects to the admin login page.
    """
    # Clear the admin_id from session
    if 'admin_id' in request.session:
        del request.session['admin_id']

    # Display a success message
    messages.success(request, "You have been logged out successfully.")

    # Redirect to the login page
    return redirect("admin_login")
