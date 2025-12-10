from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from tables.models import Table, TableOrder
from orders.models import Order
from .models import TableArchive
from django.shortcuts import redirect, render
from django.db.models import Max
from admin_auth.views import admin_required # Middleware to restrict access to admin users only

# Archive all TableOrders associated with the table.
# This ensures that previous orders are hidden when a new customer occupies the table.
# Admins are advised to archive the table once a new customer is seated,
# so the new customer won't see the previous customer's orders.
@admin_required
def archive_and_delete_table(request, table_id):
    # Get the table to be archived
    table= get_object_or_404(Table, id=table_id)

    # Get all TableOrders for this table
    table_orders = TableOrder.objects.filter(table=table)

    # Container for building the full archive structure
    archive_data = []

    # Loop through each table order to extract related orders and item details
    for t_order in table_orders:
        orders = Order.objects.filter(table_order=t_order)
        order_items = []

        # Extract item information from each order
        for o in orders:
            order_items.append({
                "item_name": o.item.name,
                "quantity": o.quantity,
                "total_item_price": float(o.total_item_price),
                "category": o.item.category,
            })

        # Add processed data for this table order to the archive container
        archive_data.append({
            "order_status": t_order.order_status,
            "order_time": t_order.order_time.isoformat(),
            "items": order_items
        })

    # Create a new TableArchive entry containing all extracted order data
    TableArchive.objects.create(
        table_name=table.description,
        archived_at=timezone.now(),
        total_payment=table.total_payment,
        data={"orders": archive_data}
    )

    # Delete the all orders and table orders associated with this table
    for t_order in table_orders:
        Order.objects.filter(table_order=t_order).delete()
        t_order.delete()

    # Delete the table itself from the database
    table.delete()


    # Redirect to the table overview page after successful archiving
    return redirect("table_overview")

# Function that allow to display all archive orders
@admin_required
def show_archive_data(request):
    # Get latest archive time per table
    tables = TableArchive.objects.values('table_name').annotate(
        latest_archived_at=Max('archived_at')
    ).order_by('-latest_archived_at')

    # Get the most recent archive timestamp overall
    last_archived_at = TableArchive.objects.aggregate(
        Max('archived_at')
    )['archived_at__max']

    context = {
        'tables': tables,
        'last_archived_at': last_archived_at
    }

    return render(request, 'archive_details.html', context)

# Function that show all the archive instance of the table
@admin_required
def archive_details(request, table_name):
    archives = TableArchive.objects.filter(table_name=table_name).order_by('-archived_at')

    return render(request, 'archived_tables_list.html', {
        'table_name': table_name,
        'archives': archives
    })
