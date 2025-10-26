from django.apps import AppConfig
from django.db.models.signals import post_migrate


class QrCodesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "qr_codes"

    def ready(self):
        pass
        # post_migrate.connect(run_after_migrate, sender=self)


def run_after_migrate(sender, **kwargs):
    """
    Auto-setup after migrations complete
    Creates batches A-Z and activates Batch A if none exist
    """
    from .models import QRBatch

    # Only run if no batches exist (first time setup)
    if not QRBatch.objects.exists():
        print("Setting up QR batches A-Z...")

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

        print("✓ Created batches A-Z, activated Batch A")
