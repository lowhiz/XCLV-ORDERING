import os
import uuid
from django.conf import settings
from django.core.files import File
from .models import Batch, QrCode, ValidList, InvalidList
from .utils import generate_qr_code_image


class BatchService:
    @staticmethod
    def create_batches():
        if Batch.objects.count() == 0:
            batches_to_create = []
            for i in range(ord('A'), ord('Z') + 1):
                batch_name = f"Batch{chr(i)}"
                batches_to_create.append(Batch(batchName=batch_name))
            Batch.objects.bulk_create(batches_to_create)
    
    @staticmethod
    def generate_qr_codes():
        if QrCode.objects.exists():
            return
        
        batches = Batch.objects.all()
        
        for batch in batches:
            batch_folder = os.path.join(settings.MEDIA_ROOT, "qrcodes", batch.batchName)
            os.makedirs(batch_folder, exist_ok=True)

            for i in range(1, 5):
                token = f"xclv-vvip-{i}-{batch.batchName}-{uuid.uuid4()}"
                BatchService._create_qr_code(token, batch, batch_folder)
            
            for i in range(1, 8):
                token = f"xclv-vip-{i}-{batch.batchName}-{uuid.uuid4()}"
                BatchService._create_qr_code(token, batch, batch_folder)

            for i in range(1, 47):
                token = f"xclv-st-{i}-{batch.batchName}-{uuid.uuid4()}"
                BatchService._create_qr_code(token, batch, batch_folder)
    
    @staticmethod
    def _create_qr_code(token, batch, folder_path):
        file_path, file_name = generate_qr_code_image(token, batch, folder_path)
        
        with open(file_path, "rb") as f:
            QrCode.objects.create(
                unique_token=token,
                batch=batch,
                image=File(f, name=f"qrcodes/{batch.batchName}/{file_name}")
            )
    
    @staticmethod
    def invalidate_all_qr_codes():
        if not InvalidList.objects.exists():
            invalid_entries = [
                InvalidList(unique_token=code.unique_token)
                for code in QrCode.objects.all()
            ]
            InvalidList.objects.bulk_create(invalid_entries)
    
    @staticmethod
    def toggle_batch():
        batches = list(Batch.objects.all().order_by('id'))
        
        if not batches:
            return
        
        # First run: activate the first batch (Batch A)
        if not ValidList.objects.exists():
            BatchService._activate_first_batch(batches[0])
            return

        # Find and toggle to next batch
        current_batch = Batch.objects.filter(is_active=True).first()
        if not current_batch:
            return
        
        current_index = BatchService._get_batch_index(batches, current_batch)
        if current_index is None:
            return

        # Calculate next batch index (circular)
        next_index = (current_index + 1) % len(batches)
        next_batch = batches[next_index]

        # Perform the toggle
        BatchService._deactivate_batch(current_batch)
        BatchService._activate_batch(next_batch)
    
    @staticmethod
    def _activate_first_batch(batch):
        """Activate the first batch during initial setup."""
        batch.is_active = True
        batch.save()

        batch_qr_codes = QrCode.objects.filter(batch=batch)
        for code in batch_qr_codes:
            ValidList.objects.get_or_create(unique_token=code.unique_token)
            InvalidList.objects.filter(unique_token=code.unique_token).delete()
    
    @staticmethod
    def _get_batch_index(batches, target_batch):
        for i, batch in enumerate(batches):
            if batch.id == target_batch.id:
                return i
        return None
    
    @staticmethod
    def _deactivate_batch(batch):
        batch.is_active = False
        batch.save()

        for code in QrCode.objects.filter(batch=batch):
            InvalidList.objects.get_or_create(unique_token=code.unique_token)
            ValidList.objects.filter(unique_token=code.unique_token).delete()
    
    @staticmethod
    def _activate_batch(batch):
        batch.is_active = True
        batch.save()

        for code in QrCode.objects.filter(batch=batch):
            ValidList.objects.get_or_create(unique_token=code.unique_token)
            InvalidList.objects.filter(unique_token=code.unique_token).delete()