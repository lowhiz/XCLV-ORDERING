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
# Global toggle variable
MENU_CLOSED = False

def view_menu(request):
    """
    Unified view for displaying menu items.
    - Customer: shows menu based on the table linked to QR.
    - Admin: shows full menu view for management.
    """

    # Determine if request comes from a customer or admin
    table_id = request.GET.get('table_id')
    is_admin = request.GET.get('admin') == 'true'  # /menu/view?admin=true

    
    # Check if menu is closed
    if MENU_CLOSED and not request.GET.get('admin'):
        return render(request, 'menu/menu_closed.html')
    
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

def table_details(request):
    """
    Display table details including running bill and order history.
    Shows all orders for the current table session.
    """
    # Get table information from session
    table_id = request.session.get('active_table_id')
    if not table_id:
        messages.error(request, 'Invalid request. Try again by scanning your table\'s QR code.')
        return redirect('/')
    
    # Fetch the table
    table = get_object_or_404(Table, id=table_id)
    
    # Get all table orders for this table (ordered by time, newest first)
    table_orders = TableOrder.objects.filter(table=table).order_by('-order_time')
    
    # Prepare order history with items
    order_history = []
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
        
        order_history.append({
            'table_order_db_id': table_order.id,  # Database ID for URL
            'table_order_id': table_order.table_order_id,  # UUID for display
            'order_time': table_order.order_time,
            'order_status': table_order.order_status,
            'items': items_list,
            'order_total': order_total
        })
    
    context = {
        'table_display': table.description,
        'table_id': table.id,
        'running_bill': table.total_payment,
        'order_history': order_history,
        'table_status': 'Active' if table.table_status else 'Inactive'
    }
    
    return render(request, 'menu/table_details.html', context)

def close_menu(request):
    """
    Prevents customers from accessing the menu.
    Admin can toggle this state.
    """
    global MENU_CLOSED
    MENU_CLOSED = True
    messages.success(request, "Menu has been closed for customers.")
    return redirect('qr_management')

def open_menu(is_open: bool):
    """Helper to toggle global menu availability."""
    global MENU_CLOSED
    MENU_CLOSED = not is_open