from django.db import models
import uuid
class Table(models.Model):
    table_id_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    table_order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='tables')
    qrcode = models.ForeignKey('qr_codes.QrCode', on_delete=models.CASCADE, related_name='tables')
    description = models.CharField(max_length=255)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.table_id_number) 
class TableOrder(models.Model):
    table_order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='table_orders')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='table_orders')
    order_time = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=255)

    def __str__(self):
        return str(self.table_order_id)
