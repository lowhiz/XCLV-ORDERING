from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import TableOrder, Table
from orders.models import Order

# This section will get all the TableOrder who have a pending status
def pending_table_orders(request):
    """
    Display all pending TableOrders with their Orders.
    """
    pending_orders = TableOrder.objects.filter(order_status__iexact="pending").order_by("-order_time")

    table_orders_with_items = []

    for table_order in pending_orders:
        # Table description from Table entity
        table_description = table_order.table.description or str(table_order.table.table_id_number)

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
    return render(request, "tables/index.html", context)

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

# This section retrieves all active tables and checks the status of their corresponding TableOrders.
# - If any TableOrder linked to a Table has a 'Pending' status,
#   the Table will be displayed as having a pending order.
# - If all associated TableOrders are marked as 'Completed',
#   the Table will be shown as having completed orders.
# - If all TableOrders are marked as 'Archived',
#   the Table will be displayed as inactive.
def table_overview(request):
    # Fetch only active tables
    active_tables = Table.objects.filter(table_status=True)

    tables_status = []  # List to hold table data and status

    for table in active_tables:
        # Get all orders for this specific table
        table_orders = TableOrder.objects.filter(table=table)

        # Default status
        status = "No Orders"

        if table_orders.exists():
            # Extract all statuses of TableOrders
            statuses = list(table_orders.values_list('order_status', flat=True))

            if any(s == "Pending" for s in statuses):
                status = "Pending"
            elif all(s == "Completed" for s in statuses):
                status = "Completed"
            elif all(s == "Archived" for s in statuses):
                status = "Inactive"
            else:
                # Mixed statuses → use the latest TableOrder’s status
                latest_order = table_orders.first()
                status = latest_order.order_status
        else:
            # No orders at all
            status = "Inactive"

        # Add to list for rendering
        tables_status.append({
            "table": table,
            "status": status,
        })

    # Render the overview page with table status data
    context = {"tables_status": tables_status}
    return render(request, "tables/table_overview.html", context)

def table_status_api(request):
    """
    API endpoint to get live table status for all active tables
    Returns JSON with table descriptions and their current status
    """
    active_tables = Table.objects.filter(table_status=True)
    table_statuses = {}

    for table in active_tables:
        # Get all orders for this specific table
        table_orders = TableOrder.objects.filter(table=table)

        # Determine status based on orders
        has_pending = False

        if table_orders.exists():
            statuses = list(table_orders.values_list('order_status', flat=True))
            has_pending = any(s.lower() == "pending" for s in statuses)

        # Use table description as key (VVIP 1, ST 1, etc.)
        table_key = table.description
        table_statuses[table_key] = {
            'has_pending_orders': has_pending,
            'status': 'pending' if has_pending else 'available'
        }

    return JsonResponse(table_statuses)
