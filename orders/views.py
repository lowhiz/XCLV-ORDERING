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
    Handle order creation:
    - TableOrder acts as the cart
    - Order represents each item in the TableOrder
    - Updates Table's total_payment
    """

    # ------------------- VALIDATE SESSION -------------------
    validated_qr_id = request.session.get('active_qr_hash')
    if not validated_qr_id:
        return JsonResponse({'error': 'No valid QR session'}, status=403)

    # ------------------- CHECK REQUEST METHOD -------------------
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    # ------------------- PARSE JSON -------------------
    try:
        data = json.loads(request.body)
        items = data.get("items", [])
        table_id = data.get("table_id")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    # ------------------- VALIDATE INPUT -------------------
    if not table_id:
        return JsonResponse({'error': 'Table ID is required'}, status=400)

    if not items or not isinstance(items, list):
        return JsonResponse({'error': 'No items in order or invalid format'}, status=400)

    # ------------------- FETCH TABLE -------------------
    table = get_object_or_404(Table, id=table_id)

    # ------------------- INITIALIZE TOTAL -------------------
    table_total = Decimal('0.00')

    # ------------------- CREATE TABLEORDER -------------------
    table_order = TableOrder.objects.create(
        table=table,
        order_status="pending"
    )

    # ------------------- CREATE ORDERS -------------------
    for item_data in items:
        item_id = item_data.get("id")
        quantity = int(item_data.get("quantity", 0))
        price = item_data.get("price", 0)

        # Validate item_id and price
        if not item_id:
            continue  # skip invalid item

        try:
            menu_item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            continue  # skip invalid item

        try:
            price = Decimal(str(price))
        except:
            price = menu_item.unit_price  # fallback to default price

        if quantity <= 0:
            continue  # skip items with zero quantity

        Order.objects.create(
            table_order=table_order,
            item=menu_item,
            quantity=quantity,
            total_item_price=price * quantity
        )

        table_total += price * quantity

    # ------------------- UPDATE TABLEORDER AND TABLE -------------------
    table_order.total_order_price = table_total
    table_order.save()

    # Do NOT add to table.total_payment here; only on completion
    # table.total_payment += table_total
    # table.save()

    # ------------------- STORE LAST ORDER IN SESSION -------------------
    request.session['last_order'] = {
        'table_order_id': str(table_order.id),
        'table_id': table.id,
        'table_display': table.description,
        'order_total': float(table_total),
        'items_count': len([i for i in items if i.get("quantity", 0) > 0])
    }

    # ------------------- RETURN SUCCESS -------------------
    return JsonResponse({
        'success': True,
        'redirect_url': '/orders/order-success/'
    })

def order_success(request):
    """
    Display order success page with details from the last order.
    """
    # Get order details from session
    last_order = request.session.get('last_order')
    if not last_order:
        # If no order in session, redirect to menu
        messages.error(request, 'No recent order found.')
        return redirect('view_menu')

    # Clear the order from session after displaying
    del request.session['last_order']

    context = {
        'table_display': last_order.get('table_display', 'Unknown Table'),
        'table_id': last_order.get('table_id'),             # table.id conflicts with delimiting characters
        'order_total': last_order.get('order_total', 0),
        'items_count': last_order.get('items_count', 0),
        'table_order_id': last_order.get('table_order_id')  # table_order.id conflicts with delimiting characters
    }

    return render(request, 'customer_order_success.html', context)


def past_order_details(request, order_id):
    """
    Display details of a specific table order (cart) with all its items.
    Only allows access to orders from the user's current validated QR session.
    """
    # Security check: Validate QR session
    validated_qr_hash = request.session.get('active_qr_hash')
    if not validated_qr_hash:
        messages.error(request, 'No valid QR session. Please scan a QR code first.')
        return render(request, 'orders/error.html', {
            'error_message': 'No valid QR session. Please scan a QR code first.'
        })

    # Get the table order
    table_order = get_object_or_404(TableOrder, id=order_id)
    table = table_order.table

    # Security check: Ensure the order belongs to the current session's table
    try:
        # Find the QRCode associated with the current session
        from qr_codes.models import QRCode
        current_qr = QRCode.objects.get(qr_hash=validated_qr_hash)

        # Check if the table order belongs to the same table as the QR code
        if table.qrcode != current_qr:
            messages.error(request, 'You can only view orders from your current table.')
            return render(request, 'orders/error.html', {
                'error_message': 'You can only view orders from your current table.'
            })

    except QRCode.DoesNotExist:
        messages.error(request, 'Invalid QR session.')
        return render(request, 'orders/error.html', {
            'error_message': 'You can only view orders from your current table.'
        })

    # Get all orders (items) in this table order
    orders = Order.objects.filter(table_order=table_order)

    # Calculate order total
    order_total = sum(order.total_item_price for order in orders)

    # Prepare items list
    items_list = []
    for order in orders:
        items_list.append({
            'name': order.item.name,
            'quantity': order.quantity,
            'unit_price': order.item.unit_price,
            'total_item_price': order.total_item_price
        })

    context = {
        'table_display': table.description,
        'table_id': table.id,
        'table_order_id': table_order.id,
        'order_time': table_order.order_time,
        'order_status': table_order.order_status,
        'items': items_list,
        'order_total': order_total,
    }
    return render(request, 'customer_order_details.html', context)
    return JsonResponse({'success': True, 'message': 'Order placed successfully!'})

# This section deletes the customer's order when they request the admin to remove it.
def delete_order(request, table_order_id):  # Changed from 'response' to 'request'
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

    # Update table total payment ONLY if the order was Completed
    if table_order.order_status.lower() == "completed":
        if table.total_payment is not None:
            table.total_payment -= total_deduction
            if table.total_payment < 0:
                table.total_payment = 0
            table.save()

    # Delete the Table order
    table_order.delete()

    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'pending_table_orders'))

# This section sets the status of the TableOrder
# after the admin reviews it and finds no issues with the customer's order.
def complete_order(request, table_order_id):
    # Fetch the specific TableOrder
    table_order = get_object_or_404(TableOrder, id=table_order_id)

    # Update the status to complete
    table_order.order_status = "Completed"
    table_order.save()

    # Add this order's total to the table's total_payment on completion
    table = table_order.table
    table.total_payment += table_order.total_order_price
    table.save()

    return redirect(request.META.get('HTTP_REFERER', 'pending_table_orders'))

@csrf_exempt
def update_order(request):
    """
    Update an existing order (admin functionality).
    Replaces all items in a TableOrder with new quantities.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        table_order_id = data.get("table_order_id")
        items = data.get("items", [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    if not table_order_id:
        return JsonResponse({'error': 'Table order ID is required'}, status=400)

    try:
        table_order = TableOrder.objects.get(id=table_order_id)
    except TableOrder.DoesNotExist:
        return JsonResponse({'error': 'Table order not found'}, status=404)

    # Delete existing orders
    Order.objects.filter(table_order=table_order).delete()

    # Calculate new total
    new_total = Decimal('0.00')
    old_order_total = table_order.total_order_price

    # Create new orders
    for item_data in items:
        item_id = item_data.get("id")
        quantity = int(item_data.get("quantity", 0))
        price = Decimal(str(item_data.get("price", 0)))

        if quantity > 0:
            menu_item = Item.objects.get(id=item_id)

            Order.objects.create(
                table_order=table_order,
                item=menu_item,
                quantity=quantity,
                total_item_price=price * quantity
            )
            new_total += price * quantity

    # Update the TableOrder's own total
    table_order.total_order_price = new_total
    table_order.save()

    # If the order is Completed, adjust the table total by the delta.
    # If Pending, do not change table.total_payment.
    if table_order.order_status.lower() == "completed":
        table = table_order.table
        table.total_payment += (new_total - old_order_total)
        if table.total_payment < 0:
            table.total_payment = 0
        table.save()

    return JsonResponse({'success': True, 'message': 'Order updated successfully!'})

def review_order(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    # Assuming you have a session or QR validation
    validated_qr_id = request.session.get('active_qr_hash')

    # Get the latest TableOrder for this table
    try:
        table_order = TableOrder.objects.filter(table=table).latest('order_time')
        orders = table_order.orders.all()
    except TableOrder.DoesNotExist:
        table_order = None
        orders = []

    # Calculate total
    total = sum([o.total_item_price for o in orders]) if orders else Decimal('0.00')

    context = {
        'table_id': table.id,
        'table_display': table.description,
        'validated_qr_id': validated_qr_id,
        'orders': orders,
        'total': total,
    }

    return render(request, 'orders/review_order.html', context)
