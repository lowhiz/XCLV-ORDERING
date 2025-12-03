from django.apps import AppConfig

class QrCodesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "qr_codes"

    # This section imports signals.py so that special actions like
    # creating batches, generating QR codes, and activating QR batches
    # are automatically run when the system starts.
    # These actions help ensure the QR code system works correctly and securely.
    def ready(self):
        from . import signals