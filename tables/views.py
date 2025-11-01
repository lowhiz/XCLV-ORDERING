from decimal import Decimal
from django.shortcuts import render
from .models import TableOrder

def pending_table_orders(request):
    """
    Display all pending TableOrders with their Orders.
    """
    pending_orders = TableOrder.objects.filter(order_status__iexact="pending").order_by("-order_time")

    table_orders_with_items = []

    for table_order in pending_orders:
        print(f"TableOrder ID: {table_order.id}")
        print(f"Linked Order ID: {table_order.table.id}")
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
