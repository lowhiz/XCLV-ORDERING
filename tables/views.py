# tables/views.py
from django.shortcuts import render, redirect
from .models import TableOrder

def pending_table_orders(request):
    """
    Displays all pending table orders for the admin dashboard.
    - Fetches orders with a status of 'pending'.
    - Orders are sorted by order time, showing the latest first.
    - Passes the data to the template for display.
    """

    # Retrieve all table orders where the order_status is 'pending'
    pending_orders = TableOrder.objects.filter(order_status__iexact="pending").order_by("-order_time")

    # Prepare data to be sent to the HTML template
    context = {
        "pending_orders": pending_orders
    }

    #Render the template that lists all pending table orders
    return render(request, "tables/index.html", context)

