from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import QRBatch, QRCode
from .services import QRBatchService
from .views import toggle_batch

@receiver(post_migrate)
def run_after_migrate(sender, **kwargs):
    """
    Run setup logic after migrations are done.
    
    - Only run this for the 'qr_codes' app.
    - If there are no QR batches in the database, create them.
    - If there are no QR codes in the database, generate them.
    - Toggle the batch status (e.g., activate the first batch).
    
    These steps ensure the QR code system is ready to use immediately after setup.
    """
    if sender.name != "qr_codes":
        return
    if not QRBatch.objects.exists():
        QRBatchService.create_all_batches()

    if not QRCode.objects.exists():
        QRBatchService.generate_all_qr_codes()
        toggle_batch()
