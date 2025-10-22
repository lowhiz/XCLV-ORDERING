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
    def activate_batch(cls, batch_name):
        current_batch = cls.get_active_batch()
        all_batches = list(cls.objects.all().order_by('batch_name'))
        return batch


class Batch(models.Model):
    batchID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) #Batch Unique Id
    batchName = models.CharField(max_length=16, unique=True) #Batch A to Batch Z
    batchStatus = models.BooleanField(default=False)    #Batch status

    def __str__(self):
        return self.batchName

class QrCode(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='qrcodes')
    image = models.ImageField(upload_to='qrcodes/')

    def __str__(self):
        return self.unique_token

class ValidList(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.unique_token

class InvalidList(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.unique_token
