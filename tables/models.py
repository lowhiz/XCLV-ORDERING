from django.db import models
import uuid

class Table(models.Model):
    qrcode = models.ForeignKey('qr_codes.QRCode', on_delete=models.CASCADE, related_name='tables')
    description = models.CharField(max_length=255)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    table_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.description or self.table_id_number}"


class TableOrder(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    order_time = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=255, default='Pending')
    total_order_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"TableOrder {self.table_order_id} for Table {self.table}"