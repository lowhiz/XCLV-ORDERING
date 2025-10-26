# About this folder
This is for database population otherwise impossible with Django's built-in fixtures system.

## Importing QR Code data to the database
First enter the Django shell via `python manage.py shell`.

Then run the following commands:

```python
from qr_codes.models import QRBatch

# Create all batches A-Z
batches = []
for i in range(ord('A'), ord('Z') + 1):
    batch_name = f"Batch {chr(i)}"
    batches.append(QRBatch(batch_name=batch_name))

QRBatch.objects.bulk_create(batches)

# Activate Batch A by default
batch_a = QRBatch.objects.get(batch_name="Batch A")
batch_a.is_active = True
batch_a.save()

print(f"✓ Created {QRBatch.objects.count()} batches")
print(f"✓ Active batch: {QRBatch.get_active_batch()}")
exit()
```
