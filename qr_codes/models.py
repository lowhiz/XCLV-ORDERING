from ftplib import all_errors
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid #for unique identifier
import hashlib

class QRBatch(models.Model):
    """
    QR Code Batches (A-Z) - Only one can be active at a time
    """

    # Batch Unique ID
    batch_ID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Batch Name (A-Z)
    batch_name = models.CharField(max_length=16, unique=True)

    # Batch Status (Active/Inactive)
    is_active = models.BooleanField(default=False, help_text="Only one batch can be active at a time")

    # Verbose via Meta class
    class Meta:
        verbose_name = "QR Code Batch"
        verbose_name_plural = "QR Code Batches"
        ordering = ['-batch_name']

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"Batch {self.batch_name} ({status})"

    def save(self, *args **kwargs):
        # Ensure only one batch is active at a time
        if self.is_active:
            QRBatch.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_batch(cls):
        return cls.objects.filter(is_active=True).first()


    # Close the current batch and activate the next batch (e.g. A -> B; A closes, B opens)

    @classmethod
    def activate_next_batch(cls):
        current_batch = cls.get_active_batch()
        all_batches = list(cls.objects.all().order_by('batch_name'))

        if not all_batches:
            return None

        if not current_batch:
            # If no batch is active, activate the first batch
            next_batch = all_batches[0]
        else:
            # Find index of current batch and get the next one (O-notation forecast: O(n))
            try:
                current_index = all_batches.index(current_batch)
                next_index = (current_index + 1) % len(all_batches)
                next_batch = all_batches[next_index]
            except ValueError:
                # Fallback to first batch if current not found (same as line 53)
                next_batch = all_batches[0]

        # Finally, deactivate current batch
        if current_batch:
            current_batch.is_active = False
            current_batch.save()


        # Activate the next batch
        next_batch.is_active = True
        next_batch.save()

        return next_batch

class QRCode(models.Model):
    """
    Individual QR Codes representing tables
    Each QR code can be used infinitely until its batch is closed
    """

    # Unique Token; pre-generated human-readable token
    unique_token = models.CharField(max_length=255, unique=True)

    # Pre-generated static hash used in QR code URLs
    qr_hash = models.CharField(max_length=64, unique=True, db_index=True)

    # Files/Images of the QR code
    image = models.ImageField(upload_to='qrcodes/')

    # Relationships
    batch = models.ForeignKey('QRBatch', on_delete=models.CASCADE, related_name='qr_codes')

    """
    def __str__(self):
        batch_status = "🟢" if self.is_currently_valid else "🔴"
        return f"{batch_status} {self.unique_token}"
    """

    def __str__(self):
        return self.unique_token

    @property
    def is_currently_valid(self):
        # Checks if this QR code is currently valid based on its batch and whether that batch is active or not
        return self.batch.is_active

    @property
    def qr_url(self):
        # Generate the full QR code URL that goes in the QR image
        ##  This uses the pre-generated static hash
        return f"https://xclv-ordering.com/order?qr={self.qr_hash}"

    @classmethod
    def get_by_hash(cls, qr_hash):
        # Get QR code by hash, return None if not found
        try:
            return cls.objects.get(qr_hash=qr_hash)
        except cls.DoesNotExist:
            return None

    @property
    def current_table(self):
        # Get the table associated with this QR code (from tables app)
        ## This will work with the tables.Table model that has:
        ## qrcode = models.ForeignKey('qr_codes.QrCode', ...)
        return getattr(self, 'tables', None)


class ValidationAttempt(models.Model):
    """
    Log all QR code validation attempts
    Tracks every time someone tries to access the system via QR
    """

    class ResultChoices(models.TextChoices):
        SUCCESS = 'success', 'Success - Valid QR & Location'
        QR_NOT_FOUND = 'qr_not_found', 'QR Hash Not Found'
        BATCH_INACTIVE = 'batch_inactive', 'Batch Not Currently Active'
        LOCATION_INVALID = 'location_invalid', 'Location Outside Geofence'
        LOCATION_ERROR = 'location_error', 'Location Service Error'
        LOCATION_DENIED = 'location_denied', 'User Denied Location Permission'

    class Meta:
        verbose_name = "Validation Attempt"
        verbose_name_plural = "Validation Attempts"
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['-attempted_at']),
            models.Index(fields=['result', '-attempted_at']),
            models.Index(fields=['qr_code', '-attempted_at']),
            models.Index(fields=['ip_address', '-attempted_at']),
        ]

    # QR Code being validated (can be null if QR hash not found)
    qr_code = models.ForeignKey(
        'QRCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validation_attempts'
    )

    # Raw QR hash from the request (always logged even if invalid)
    qr_hash_attempted = models.CharField(
        max_length=64,
        help_text="The QR hash that was attempted"
    )

    # Location data (from geolocation check)
    user_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    user_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    distance_from_club = models.FloatField(
        null=True,
        blank=True,
        help_text="Distance in meters from club location"
    )

    # Validation result
    result = models.CharField(
        max_length=20,
        choices=ResultChoices.choices
    )

    error_message = models.TextField(
        blank=True,
        help_text="Detailed error message if validation failed"
    )

    # Request metadata (for security monitoring)
    # ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text="Django session key for tracking user flow"
    )

    # Timestamps
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status_emoji = "✅" if self.result == self.ResultChoices.SUCCESS else "❌"
        qr_display = self.qr_code.unique_token if self.qr_code else self.qr_hash_attempted[:12] + "..."

        return f"{status_emoji} {qr_display} - {self.get_result_display()}"

    @property
    def is_successful(self):
        return self.result == self.ResultChoices.SUCCESS

    @property
    def formatted_location(self):
        if self.user_latitude and self.user_longitude:
            return f"({self.user_latitude}, {self.user_longitude})"
        return "No location data"

    @property
    def formatted_distance(self):
        if self.distance_from_club is not None:
            if self.distance_from_club < 1000:
                return f"{self.distance_from_club:.0f}m"
            else:
                return f"{self.distance_from_club/1000:.1f}km"
        return "Unknown distance"

class ValidList(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.unique_token

class InvalidList(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.unique_token
