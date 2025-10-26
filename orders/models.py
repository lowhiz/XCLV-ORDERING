from django.db import models
import uuid
class Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    item = models.ForeignKey('menu.Item', on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField()
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.order_id)