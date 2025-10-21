from django.apps import AppConfig
from django.db.models.signals import post_migrate


class QrCodesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "qr_codes"

    def ready(self):
        post_migrate.connect(run_after_migrate, sender=self)


def run_after_migrate(sender, **kwargs):
    from .services import BatchService
    from .models import Batch, ValidList

    BatchService.create_batches()
    BatchService.generate_qr_codes()
    BatchService.invalidate_all_qr_codes()
    if not ValidList.objects.exists():
        first_batch = Batch.objects.order_by("id").first()
        if first_batch:
            BatchService._activate_first_batch(first_batch)
