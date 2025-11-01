import json
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Item
from django.shortcuts import render, get_object_or_404
from tables.models import Table, TableOrder
from orders.models import Order
from .models import Item
from django.views.decorators.csrf import csrf_exempt


def view_menu(request):
    """
    Unified view for displaying menu items.
    - Customer: shows menu based on the table linked to QR.
    - Admin: shows full menu view for management.
    """

    # Determine if request comes from a customer or admin
    table_id = request.GET.get('table_id')
    is_admin = request.GET.get('admin') == 'true'  # /menu/view?admin=true

    # Fetch all menu items and group them by category
    items = Item.objects.all().order_by('category', 'name')
    categories = {}
    for item in items:
        categories.setdefault(item.category, []).append(item)

    # Base context shared between admin and customer
    context = {'categories': categories}

    if table_id:
        table = get_object_or_404(Table, id=table_id)
        qr_hash = table.qrcode.qr_hash if table.qrcode else None

        # Use session keys that match order_review
        request.session['active_table_id'] = table.id
        request.session['active_table_display'] = table.description
        request.session['active_qr_hash'] = getattr(table.qrcode, 'qr_hash', None)


        context.update({
            'table_id': table.id,
            'table_display': table.description,
            'qr_hash': qr_hash,
        })
        return render(request, 'menu/menu_list.html', context)

    elif is_admin:  # Admin view (dashboard)
        return render(request, 'menu/admin.html', context)

    # Fallback: customer-style view without a specific table
    return render(request, 'menu/menu_list.html', context)

def order_review(request):
    """
    Display order review page where customers confirm their order
    """
   
    # Validates QR/auth session
    validated_qr_id = request.session.get('active_qr_hash')
    if not validated_qr_id:
        messages.error(request, 'Invalid request. Try again by scanning your table\'s QR code.')
        return redirect('/')

    # Get table information from session
    table_display = request.session.get('active_table_display', 'Unknown Table')
    table_id = request.session.get('active_table_id', 'Unknown')
    context = {
        'table_display': table_display,
        'table_id': table_id,
        'validated_qr_id': validated_qr_id,
    }

    return render(request, 'menu/order_review.html', context)

@csrf_exempt
def create_order(request):
    """
    Handle order creation and store into TableOrder/Table/Order models.
    Debug prints enabled to show data being processed.
    """

    print("==== create_order called ====")

    # Validate QR/auth session from the current session
    validated_qr_id = request.session.get('active_qr_hash')
    print("Validated QR ID from session:", validated_qr_id)
    if not validated_qr_id:
        print("No valid QR session")
        return JsonResponse({'error': 'No valid QR session'}, status=403)

    # Ensure the request method is POST
    print("Request method:", request.method)
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    # Parse JSON payload
    try:
        data = json.loads(request.body)
        items = data.get("items", [])
        table_id = data.get("table_id")
        print("Parsed JSON data:", data)
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    # Validate table_id and items
    print("Table ID:", table_id)
    print("Items received:", items)
    if not table_id:
        print("No table_id provided")
        return JsonResponse({'error': 'Table ID is required'}, status=400)

    if not items or not isinstance(items, list):
        print("No items or invalid format")
        return JsonResponse({'error': 'No items in order or invalid format'}, status=400)

    # Fetch the Table object
    try:
        table = Table.objects.get(id=table_id)
        print("Fetched Table object:", table)
    except Table.DoesNotExist:
        print("Table not found for ID:", table_id)
        return JsonResponse({'error': 'Table not found'}, status=404)

    # Initialize total
    table_total = Decimal('0.00')

    # Create one TableOrder for this request
    table_order = TableOrder.objects.create(
        table=table,
        order_status="pending"
    )
    print("Created TableOrder (cart):", table_order)

    table_total = Decimal('0.00')

    # Create Orders linked to this TableOrder
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
        print(f"Created Order: {order} ({quantity} x {menu_item.name})")

        table_total += price * quantity

    # Update Table total_payment
    table.total_payment += table_total
    table.save()

    return JsonResponse({'success': True, 'message': 'Order placed successfully!'})
