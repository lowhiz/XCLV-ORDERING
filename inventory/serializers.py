from rest_framework import serializers
from menu.models import Item

class InventoryItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = Item
    fields = ['id', 'name', 'category', 'unit_price', 'is_available']
    read_only_fields = ['id', 'name', 'category', 'unit_price']
    # Only is_available can be written through the API.
    # Pricing and naming are managed separately.
