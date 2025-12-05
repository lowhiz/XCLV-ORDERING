from django.db import models
class Item(models.Model):
    """
    Model representing a single item or product available for order 
    This model serves as the core inventory or price list reference.
    """
    
    # Classification for grouping similar items.
    category = models.CharField(max_length=255)
    
    # The common, display name of the item.
    name = models.CharField(max_length=255)
    
    # An explanation or detailing of the item.
    description = models.TextField()

    # The selling price of one unit of this item.
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """
        Returns the name of the item for a readable representation of the object.
        """
        return self.name