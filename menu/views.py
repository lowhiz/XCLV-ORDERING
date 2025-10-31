from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Item
from django.shortcuts import render, get_object_or_404
from tables.models import Table
from .models import Item

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

    if table_id:  # Customer view (linked to a table)
        table = get_object_or_404(Table, id=table_id)
        context.update({
            'table_id': table.id,
            'table_display': table.description,
        })
        return render(request, 'menu/menu_list.html', context)

    elif is_admin:  # Admin view (dashboard)
        return render(request, 'menu/admin.html', context)

    # Fallback: customer-style view without a specific table
    return render(request, 'menu/menu_list.html', context)


def create_order(request):
    """
    Handle order creation from menu
    """

    # Check QR validation
    validated_qr_id = request.session.get('validated_qr_id')
    if not validated_qr_id:
        return JsonResponse({'error': 'No valid QR session'}, status=403)

    if request.method == 'POST':
        # Handle order creation logic here
        # You'll integrate with your orders app

        # After successful order, optionally clear the session or keep it for more orders
        # request.session.pop('validated_qr_id', None)

        return JsonResponse({'success': True, 'message': 'Order placed successfully!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)
