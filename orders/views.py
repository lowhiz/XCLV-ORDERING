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

# Create your views here.
# here dapat si create_order
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
