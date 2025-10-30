import os
import uuid
import hashlib
from django.conf import settings
from django.core.files import File
from .models import QRBatch, QRCode
from .utils import generate_qr_code_image

#This class handles how QR Code batches works
class QRBatchService:
    """
    Create QR batches named 'Batch A' to 'Batch Z' if none exist.

    - Checks if the QRBatch table is empty. If so, proceeds to create batches.
    - Uses ASCII values to iterate from 'A' to 'Z'.
    - Prepares a list of QRBatch objects with names "Batch A" to "Batch Z".
    - Inserts all batches at once using bulk_create for efficiency.
    """

    @staticmethod
    def create_all_batches():
        """Create all batches A-Z if they don't exist"""
        if QRBatch.objects.count() == 0:
            batches_to_create = []
            for i in range(ord('A'), ord('Z') + 1):
                batch_name = f"Batch {chr(i)}"
                batches_to_create.append(QRBatch(batch_name=batch_name))
            QRBatch.objects.bulk_create(batches_to_create)

    @staticmethod
    def generate_all_qr_codes():
        """
        Generate QR codes for all batches if they don't already exist.

        - Checks if any QR codes exist in the database; if so, the function exits.
        This ensures QR codes are only pre-generated once per batch setup.

        - Iterates through all QR batches.

        - Creates a folder for each batch inside MEDIA_ROOT/qrcodes/<batch_name>.

        - Generates QR codes for different table types:
            * VVIP tables: 1-4
            * VIP tables: 1-7
            * Standard tables: 1-46

        - Each QR code token format:
            "<prefix>-<table_number>-<batch_name>-<UUID>"
            Example: "xclv-vvip-1-BatchA-550e8400-e29b-41d4-a716-446655440000"

        - Calls QRBatchService._create_qr_code() to create the QRCode object and save the image.
        """

        if QRCode.objects.exists():
            return

        batches = QRBatch.objects.all()

        for batch in batches:
            batch_folder = os.path.join(settings.MEDIA_ROOT, "qrcodes", batch.batch_name.replace(' ', ''))
            os.makedirs(batch_folder, exist_ok=True)

            # VVIP tables (1-4)
            for i in range(1, 5):
                token = f"xclv-vvip-{i}-{batch.batch_name.replace(' ', '')}-{uuid.uuid4()}"
                QRBatchService._create_qr_code(token, batch, batch_folder)

            # VIP tables (1-7)
            for i in range(1, 8):
                token = f"xclv-vip-{i}-{batch.batch_name.replace(' ', '')}-{uuid.uuid4()}"
                QRBatchService._create_qr_code(token, batch, batch_folder)

            # Standard tables (1-46)
            for i in range(1, 47):
                token = f"xclv-st-{i}-{batch.batch_name.replace(' ', '')}-{uuid.uuid4()}"
                QRBatchService._create_qr_code(token, batch, batch_folder)
    
    @staticmethod
    def _create_qr_code(token, batch, folder_path):
        """
        Create a single QRCode object and save its image.

        - Ensures the folder path exists for storing the QR image.
        - Generates a SHA256 hash of the token for secure identification.
        - Calls generate_qr_code_image() to create the actual QR image.
        - Saves a new QRCode instance in the DB with:
            * unique_token: human-readable token
            * batch: associated QRBatch
            * qr_hash: secure hashed token
            * image: File object pointing to generated QR image
        """
        if folder_path is None:
            folder_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', batch.batch_name)
        os.makedirs(folder_path, exist_ok=True)

        qr_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        file_path, file_name = generate_qr_code_image(token, qr_hash, batch, folder_path)

        with open(file_path, "rb") as f:
            QRCode.objects.create(
                unique_token=token,
                batch=batch,
                qr_hash=qr_hash,
                image=File(f, name=f"{batch.batch_name.replace(' ', '')}/{file_name}")
            )

    @staticmethod
    def toggle_batch():
        """
        Toggle the active QR batch.

        Rules:
        - Only one batch can be active at a time (batch_status=True).
        - If no batch is currently active, activate the first batch.
        - If a batch is active, deactivate it and activate the next batch in order.
        - The toggle is circular: after the last batch, it wraps back to the first.

        Steps:
        1. Get all batches ordered by ID.
        2. Find the currently active batch.
        3. If no batch is active, activate the first one.
        4. Otherwise, find the index of the current batch.
        5. Determine the next batch using modulo for circular rotation.
        6. Deactivate current batch and activate the next batch.
        """
        
        batches = list(QRBatch.objects.all().order_by('id'))
        if not batches:
            return

        # Find currently active batch
        current_batch = QRBatch.objects.filter(batch_status=True).first()

        if not current_batch:
            # If no batch is active yet, activate the first one
            first_batch = batches[0]
            first_batch.batch_status = True
            first_batch.save()
            return

        # Find index of the current active batch
        current_index = next((i for i, b in enumerate(batches) if b.id == current_batch.id), None)
        if current_index is None:
            return

        # Determine next batch (circular toggle)
        next_index = (current_index + 1) % len(batches)
        next_batch = batches[next_index]

        # Deactivate current and activate next
        current_batch.batch_status = False
        current_batch.save()

        next_batch.batch_status = True
        next_batch.save()