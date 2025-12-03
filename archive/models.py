from django.db import models

class TableArchive(models.Model):
    """
    This model isolates past order data from active transactions to ensure
    data privacy, operational clarity, and clean table turnover. Once a table
    is closed and payment is completed, the associated order details are moved
    into this archive. This prevents the next customer from seeing any previous
    orders and allows the system to reset the table for new use.
    """

    # Name or identifier of the table where the order occurred.
    table_name = models.CharField(max_length=255)

    # Timestamp automatically set when the archive entry is created.
    archived_at = models.DateTimeField(auto_now_add=True)

    # Total payment for the archived order.
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)

    # JSON field storing the entire order details
    # This allows flexible structure without strict table relations.
    data = models.JSONField()

    def __str__(self):
        """String representation of the archive record."""
        return f"Archive: {self.table_name} ({self.archived_at.strftime('%Y-%m-%d %H:%M:%S')})"