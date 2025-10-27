from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Item

def menu_list(request):
    """
    Display menu items - only accessible after QR validation
    """

    # Check if user has a validated QR session
    validated_qr_id = request.session.get('validated_qr_id')
    if not validated_qr_id:
        messages.error(request, 'Please scan a QR code to access the menu.')
        return redirect('/')

    # Get table information from session
    table_display = request.session.get('current_table_display', 'Unknown Table')
    table_id = request.session.get('current_table_id', 'Unknown')

    # Get menu items
    items = Item.objects.all().order_by('category', 'name')

    # Group by category
    categories = {}
    for item in items:
        categories.setdefault(item.category, []).append(item)

    context = {
        'categories': categories,
        'table_display': table_display,
        'table_id': table_id,
        'validated_qr_id': validated_qr_id,
    }

    return render(request, 'menu/menu_list.html', context)

def order_review(request):
    """
    Display order review page where customers confirm their order
    """

    # Validates QR/auth session
    validated_qr_id = request.session.get('validated_qr_id')
    if not validated_qr_id:
        messages.error(request, 'Invalid request. Try again by scanning your table\'s QR code.')
        return redirect('/')

    # Get table information from session
    table_display = request.session.get('current_table_display', 'Unknown Table')
    table_id = request.session.get('current_table_id', 'Unknown')

    context = {
        'table_display': table_display,
        'table_id': table_id,
        'validated_qr_id': validated_qr_id,
    }

    return render(request, 'menu/order_review.html', context)


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
