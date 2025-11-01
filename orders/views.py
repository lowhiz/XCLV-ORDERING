import json
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from tables.models import Table, TableOrder
from .models import Order
from menu.models import Item
from django.views.decorators.csrf import csrf_exempt

# This section creates the customer's order.
# It is also used when the customer requests to modify their existing order.
@csrf_exempt
def create_order(request):
    """
    Handle order creation and store into Order, then Order to TableOrder, and TableOrder to Table.
    TableOrder is the Cart
    Order is the items group by it's name
    """

    # Validate QR/auth session from the current session
    validated_qr_id = request.session.get('active_qr_hash')
    if not validated_qr_id:
        return JsonResponse({'error': 'No valid QR session'}, status=403)

    # Ensure the request method is POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    # Parse JSON payload
    try:
        data = json.loads(request.body)
        items = data.get("items", [])
        table_id = data.get("table_id")
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    # Validate table_id and items
    if not table_id:
        return JsonResponse({'error': 'Table ID is required'}, status=400)
    if not items or not isinstance(items, list):
        return JsonResponse({'error': 'No items in order or invalid format'}, status=400)

    # Fetch the Table object
    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return JsonResponse({'error': 'Table not found'}, status=404)

    # Initialize total
    table_total = Decimal('0.00')

    # Create one TableOrder for this request
    table_order = TableOrder.objects.create(
        table=table,
        order_status="pending"
    )
    
    table_total = Decimal('0.00')

    # Create Order linked to TableOrder
    for i, item_data in enumerate(items, start=1):
        item_id = item_data.get("id")
        quantity = int(item_data.get("quantity", 0))
        price = Decimal(str(item_data.get("price", 0)))

        menu_item = Item.objects.get(id=item_id)

        order = Order.objects.create(
            table_order=table_order,  # link to single TableOrder
            item=menu_item,
            quantity=quantity,
            total_item_price=price * quantity
        )
        table_total += price * quantity

    # Update Table total_payment
    table.total_payment += table_total
    table.save()

    return JsonResponse({'success': True, 'message': 'Order placed successfully!'})

# This section deletes the customer's order when they request the admin to remove it.
def delete_order(response, table_order_id):
    # Fetch the specific TableOrder
    table_order = get_object_or_404(TableOrder, id=table_order_id)

    # Get the table details
    table = table_order.table

    # Get the orders of TableOrder and delete
    orders = table_order.orders.all()

    # Delete and deduct order from the table total payment
    total_deduction = 0
    for order in orders:
        total_deduction += order.total_item_price
        order.delete()

    # Update table total payment
    if table.total_payment is not None:
        table.total_payment -= total_deduction
        if table.total_payment < 0:
            table.total_payment = 0
        table.save()

    # Delete the Table order
    table_order.delete()

    return redirect("pending_table_orders")

# This section sets the status of the TableOrder
# after the admin reviews it and finds no issues with the customer's order.
def complete_order(response, table_order_id):
    # Fetch the specific TableOrder
    table_order = get_object_or_404(TableOrder, id=table_order_id)

    # Update the status to complete
    table_order.order_status = "Completed"
    table_order.save

    return redirect("pending_table_orders")

# Archive all TableOrders associated with the table.
# This ensures that previous orders are hidden when a new customer occupies the table.
# Admins are advised to archive the table once a new customer is seated,
# so the new customer won't see the previous customer's orders.
def archive_order(response, table_order_id):
    # Fetch the specific TableOrder
    table_order = get_object_or_404(TableOrder, id=table_order_id)

    # Get the table details
    table = table_order.table

    # Get the related TableOrders
    related_orders = TableOrder.objects.filter(table=table)

    # Archive all orders under the same table
    for order in related_orders:
        order.order_status = "Archived"
        order.save()
        
    # Update the table status to False
    table.table_status = False
    table.save()

    return redirect("pending_table_orders")