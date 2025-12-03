from django.db import models
import uuid  # For generating unique identifiers

# It is ideal for models.py to define only the entities (database tables)
# and their attributes (fields/columns). Business logic or other operations
# should be handled elsewhere (e.g., utils.py, services.py, or views.py).


# -----------------------------------------------------------------------------
# QRBatch Model
# -----------------------------------------------------------------------------
# Represents a batch of QR codes used in the business operation.
# Each batch can be marked as active or inactive — only one batch
# should be active at a time.
class QRBatch(models.Model):
    # Unique identifier for the batch (auto-generated UUID)
    batch_ID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Name of the batch (A–Z format, must be unique)
    batch_name = models.CharField(max_length=16, unique=True)
    
    # Indicates whether the batch is currently active
    batch_status = models.BooleanField(default=False)

    def __str__(self):
        return self.batch_name


# -----------------------------------------------------------------------------
# QRCode Model
# -----------------------------------------------------------------------------
# Represents an individual QR code within a batch.
# Each QR code has a unique token that allows the system
# to identify and validate customer orders.
class QRCode(models.Model):
    # Human-readable unique token (e.g., "xclv-vip-1-BatchA-uuid")
    unique_token = models.CharField(max_length=255, unique=True)

    # Relationship: Each QR code belongs to one batch
    batch = models.ForeignKey('QRBatch', on_delete=models.CASCADE, related_name='qr_codes')
    
    # Image file of the generated QR code
    image = models.ImageField(upload_to='qrcodes/')

    # qr_hash for user ends to prevent the exposure of unique_token
    qr_hash = models.CharField(max_length=64, null=True, blank=True)

    
    def __str__(self):
        return self.unique_token