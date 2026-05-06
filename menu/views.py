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
from admin_auth.views import admin_required

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
        table_id = request.GET.get('table_id')
        return render(request, 'customer_menu_closed.html', {
            'table_id': table_id
        })
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
        return render(request, 'customer_menu.html', context)

    elif is_admin:  # Admin view (dashboard)
        return render(request, 'admin_menu.html', context)

    # Fallback: customer-style view without a specific table
    return render(request, 'error.html', context)

def review(request):
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
    return render(request, 'customer_order_review.html', context)


def close_menu(request):
    """
    Prevents customers from accessing the menu.
    Admin can toggle this state.
    """
    global MENU_CLOSED
    MENU_CLOSED = True
    request.session["menu_closed"] = True
    messages.success(request, "Menu has been closed for customers.")
    return redirect('qr_management')

def open_menu(request):
    """Helper to toggle global menu availability."""
    global MENU_CLOSED
    MENU_CLOSED = False
    request.session["menu_closed"] = False


def admin_toggle_menu(request):
    """Opens the menu for customers from the admin side."""
    open_menu(request)
    return redirect("qr_management")

def check_menu_status(request):
    global MENU_CLOSED
    return JsonResponse({"menu_closed": MENU_CLOSED})


# New view to support the Internal Inventory API implemented via DRF
# via the "inventory" app
@admin_required
def toggle_item_availability(request, item_id):
    """
    Toggles the is_available field on a menu Item.
    Called via AJAX POST from the admin View Menu page (admin_menu.html).
    Returns JSON so the frontend can update the card live without a page reload.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=405)

    item = get_object_or_404(Item, id=item_id)
    item.is_available = not item.is_available
    item.save(update_fields=['is_available'])

    return JsonResponse({
        'success':      True,
        'item_id':      item.id,
        'item_name':    item.name,
        'is_available': item.is_available,
    })
