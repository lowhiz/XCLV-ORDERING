from orders.models import Order

def mark_items_from_completed_order(table_order):
    """
    Called after a TableOrder is marked Completed.

    Current behaviour: No automatic stock deduction (the system does not
    track stock quantities yet). This is a hook ready for future expansion.

    To auto-mark an item Out of Stock when completed, uncomment the block below.
    """
    pass

    # ----- OPTIONAL: auto-disable items with zero remaining stock -----
    # Uncomment and adapt if you add a 'stock_count' field to Item later:
    #
    # orders = Order.objects.filter(table_order=table_order).select_related('item')
    # for order in orders:
    #     item = order.item
    #     item.stock_count = max(0, item.stock_count - order.quantity)
    #     if item.stock_count == 0:
    #         item.is_available = False
    #     item.save(update_fields=['stock_count', 'is_available'])
