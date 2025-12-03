from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import TableOrder, Table
from orders.models import Order
from qr_codes.models import QRCode, QRBatch
from django.http import JsonResponse

# This section will get all the TableOrder who have a pending status
def pending_table_orders(request):
    """
    Display all pending TableOrders with their Orders.
    """
    pending_orders = TableOrder.objects.filter(order_status__iexact="pending").order_by("-order_time")

    table_orders_with_items = []

    for table_order in pending_orders:
        # Table description from Table entity
        table_description = table_order.table.description or str(table_order.table.id)

        # Get all Orders linked to the TableOrder
        orders = table_order.orders.all()

        items_list=[]
        # Collect all item details
        for order in orders:
            items_list.append({
                "name": order.item.name,
                "quantity": order.quantity,
                "total_item_price":Decimal(order.total_item_price)
            })

        table_orders_with_items.append({
            "table_order_id": table_order.id,
            "description": table_description,
            "items": items_list,
            "order_status": table_order.order_status,
            "order_time": table_order.order_time,
        })

    context = {
        "pending_orders": table_orders_with_items
    }
    return render(request, "pending_orders.html", context)

# This section will retrieve the orders of the TableOrder
def table_order_data(request, table_order_id):
    # Fetch the specific TableOrder
    table_order = get_object_or_404(TableOrder, id=table_order_id)

    # Get all orders associated with the TableOrder
    orders = table_order.orders.all()

    # Collect item details
    items_list = []
    for order in orders:
        print(f"Processing Order ID: {order.id} | Item: {order.item.name} | Qty: {order.quantity} | Total: {order.total_item_price}")
        items_list.append({
            "name": order.item.name,
            "quantity": order.quantity,
            "total_item_price": order.total_item_price,
        })

    # Prepare context for rendering
    context = {
        "table_order": table_order,
        "orders": orders,
    }

    return render(request, "orders/edit_order.html", context)

# This section retrieves all tables and checks the status of their corresponding TableOrders.
# - If any TableOrder linked to a Table has a 'Pending' status,
#   the Table will be displayed as having a pending order.
# - If all associated TableOrders are marked as 'Completed',
#   the Table will be shown as having completed orders.
# - If all TableOrders are marked as 'Archived',
#   the Table will be displayed as inactive.
def table_overview(request):
    # Get the active batch
    active_batch = QRBatch.objects.filter(batch_status=True).first()

    # Get all QR codes under that batch
    qrcodes = QRCode.objects.filter(batch=active_batch)

    # Container for table status
    tables_status = []
    
    for qr in qrcodes:
        # Get the table name based on qrcode
        table_name = qr.display_name
        
        # Find table linked to this qr, if it exist within the database(means someone already occupied the table)
        table = Table.objects.filter(description=table_name).first()

       
        if table:
             # If the table exist, get TableOrders associated
            table_orders = TableOrder.objects.filter(table=table)

            # If there is a TableOrder associated with the Table, get the status
            if table_orders.exists():
                statuses = list(table_orders.values_list('order_status', flat=True))
                if any(s == "pending" for s in statuses):
                    status = "Pending"
                elif all(s == "Completed" for s in statuses):
                    status = "Completed"
                else:
                    status = table_orders.order_by('-order_time').first().order_status
                    
            # If there is no TableOrder, marked inactive(this will happen if the customer did not choose to order or still picking up the order)
            else:
                status = "Inactive"

            # Get the table id if it is being occupied
            table_id = table.id
        
        # If the Table is being not occupied, just make the id as 0 and status as inactive
        else:
            table_id = 0
            status = "Inactive"

        # Get the details to be pass
        tables_status.append({
            "id": table_id,
            "name": qr.display_name,
            "status": status
        })
    print("\n=== FINAL TABLES STATUS LIST ===")
    for t in tables_status:
        print(t)
    # go to the table_overview with the corresponding details
    return render(request, "table_overview.html", {
        "tables_status": tables_status
    })


# This part of code will display the Total bill of the table
# the pending orders
# then the past orders
def table_description(request, table_id):
    if table_id == 0:
        return render(request, 'table_not_available.html')

    table = get_object_or_404(Table, id=table_id)

    # Get all TableOrders for this table
    table_orders = table.orders.all()

    pending_orders = []
    past_orders = []
    completed_count = 0  # Counter for completed TableOrders

    for table_order in table_orders:
        orders = table_order.orders.all()

        order_data = {
            'table_order': table_order,
            'orders': orders
        }

        if table_order.order_status.lower() == 'pending':
            pending_orders.append(order_data)
        elif table_order.order_status.lower() == 'completed':
            past_orders.append(order_data)
            completed_count += 1  # Increment the counter
        else:
            print(f"TableOrder ID {table_order.id} has unhandled status: {table_order.order_status}")

    context = {
        'table': table,
        'total_payment': table.total_payment,
        'pending_orders': pending_orders,
        'past_orders': past_orders,
        'completed_count': completed_count  # Add count to context
    }

    return render(request, 'table_description.html', context)

def edit_order(request, table_order_id):
    """
    Allow admin to edit an existing order by displaying current items
    in a similar interface to customer_menu.html with pre-populated quantities.
    """
    from menu.models import Item

    # Fetch the specific TableOrder
    table_order = get_object_or_404(TableOrder, id=table_order_id)

    # Get all current orders (items) in this table order
    current_orders = table_order.orders.all()

    # Create a dictionary of current item quantities
    current_quantities = {}
    for order in current_orders:
        current_quantities[order.item.id] = order.quantity

    # Get all menu items organized by category (same as menu_list view)
    all_items = Item.objects.all().order_by('category', 'name')
    categories = {}
    for item in all_items:
        if item.category not in categories:
            categories[item.category] = []

        # Add current quantity to each item
        item.current_quantity = current_quantities.get(item.id, 0)
        categories[item.category].append(item)

    # Calculate current order total
    current_total = sum(order.total_item_price for order in current_orders)

    context = {
        'categories': categories,
        'table_order': table_order,
        'table_display': table_order.table.description,
        'table_id': table_order.table.id,
        'current_quantities': current_quantities,
        'current_total': current_total,
        'is_admin_edit': True,  # Flag to identify this as admin edit mode
    }

    return render(request, 'tables/edit_order.html', context)

# This function is used for live updating of table statuses and incoming orders.
# While we already have table_overview to display the current status of all tables,
# this separate function is necessary for AJAX polling to reflect real-time changes
# without refreshing the page. Both functions serve distinct purposes and are not redundant.
def table_status_api(request):
    # Fetch all tables and prefetch related QRCode to reduce DB queries
    tables = Table.objects.select_related('qrcode').all()
    
    # Container to store the status of each table
    tables_status = []

    for table in tables:
        # Get all orders for this table, ordered by order_time (oldest first)
        orders = table.orders.order_by('order_time')
        
        if orders.exists():
            # Extract all order statuses in lowercase to make comparisons case-insensitive
            statuses = [o.order_status.lower() for o in orders]

            # Determine table status based on the orders
            if "pending" in statuses:
                # If any order is still pending, the table status is Pending
                status = "Pending"
            elif all(s == "completed" for s in statuses):
                # If all orders are completed, table status is Completed
                status = "Completed"
            elif all(s == "archived" for s in statuses):
                # If all orders are archived, table status is Inactive
                status = "Inactive"
            else:
                # Mixed statuses (some completed, some archived, etc.)
                # Use the latest order's status as the table status
                status = orders.last().order_status
        else:
            # No orders exist for this table, mark as Inactive
            status = "Inactive"

        # Add the table's display name and calculated status to the result list
        tables_status.append({
            "name": table.qrcode.display_name,  # Table name based on QRCode
            "status": status,                    # Determined status
        })

    # Return the table statuses as JSON for AJAX polling
    return JsonResponse(tables_status, safe=False)

def table_details(request):
    """
    Display table details including running bill and separate:
    - Ongoing orders (Preparing / Pending)
    - Completed orders (Served)
    """

    table_id = request.session.get('active_table_id')
    if not table_id:
        messages.error(request, "Invalid request. Please scan your table's QR code again.")
        return redirect('/')

    table = get_object_or_404(Table, id=table_id)

    table_orders = TableOrder.objects.filter(table=table).order_by('-order_time')

    ongoing_orders = []
    completed_orders = []

    for table_order in table_orders:
        orders = table_order.orders.all()
        items_list = []
        order_total = Decimal('0.00')

        for order in orders:
            items_list.append({
                'name': order.item.name,
                'quantity': order.quantity,
                'unit_price': order.item.unit_price,
                'total_item_price': order.total_item_price
            })
            order_total += order.total_item_price

        order_data = {
            'table_order_id': table_order.id,
            'order_time': table_order.order_time,
            'order_status': table_order.order_status,
            'items': items_list,
            'order_total': order_total
        }

        # Categorize orders
        if table_order.order_status.lower() in ['served', 'completed', 'done']:
            completed_orders.append(order_data)
        else:
            ongoing_orders.append(order_data)

    context = {
        'table_display': table.description,
        'table_id': table.id,
        'running_bill': table.total_payment,
        'ongoing_orders': ongoing_orders,
        'completed_orders': completed_orders,
        'table_status': 'Active' if table.table_status else 'Inactive'
    }

    return render(request, 'customer_table.html', context)
