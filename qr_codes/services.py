import os
import uuid
import hashlib
from django.conf import settings
from django.core.files import File
from .models import QRBatch, QRCode, ValidationAttempt
from .utils import generate_qr_code_image
from geolocation.services import GeolocationService


class QRBatchService:
    """Service for managing QR code batches"""

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
        """Generate QR codes for all batches if they don't exist"""
        if QRCode.objects.exists():
            return

        batches = QRBatch.objects.all()

        for batch in batches:
            batch_folder = os.path.join(settings.MEDIA_ROOT, "qrcodes", batch.batch_name.replace(" ", ""))
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
        """Create a single QR code with image"""
        # Generate hash from token
        qr_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()

        # Generate QR image
        file_path, file_name = generate_qr_code_image(token, qr_hash, batch, folder_path)

        # Create QR code record
        with open(file_path, "rb") as f:
            QRCode.objects.create(
                unique_token=token,
                qr_hash=qr_hash,
                batch=batch,
                image=File(f, name=f"qrcodes/{batch.batch_name.replace(' ', '')}/{file_name}")
            )


class QRValidationService:
    """Service for validating QR codes and managing the validation process"""

    @staticmethod
    def validate_entry(
        qr_hash: str,
        user_lat: float,
        user_lon: float,
        ip_address: str = None,
        user_agent: str = None,
        session_key: str = None
    ) -> dict:
        """
        Complete QR validation process including location check

        Returns dict with validation result
        """

        # Step 1: Find QR code
        qr_code = QRCode.get_by_hash(qr_hash)

        if not qr_code:
            # Log failed attempt
            ValidationAttempt.objects.create(
                qr_hash_attempted=qr_hash,
                result=ValidationAttempt.ResultChoices.QR_NOT_FOUND,
                error_message=f"QR hash '{qr_hash}' not found",
                ip_address=ip_address,
                user_agent=user_agent or '',
                session_key=session_key or ''
            )

            return {
                'success': False,
                'error': 'QR code not found',
                'result': 'qr_not_found'
            }

        # Step 2: Check if QR's batch is active
        if not qr_code.is_currently_valid:
            ValidationAttempt.objects.create(
                qr_code=qr_code,
                qr_hash_attempted=qr_hash,
                result=ValidationAttempt.ResultChoices.BATCH_INACTIVE,
                error_message=f"Batch {qr_code.batch.batch_name} is not active",
                ip_address=ip_address,
                user_agent=user_agent or '',
                session_key=session_key or ''
            )

            return {
                'success': False,
                'error': 'QR code is not currently active',
                'result': 'batch_inactive'
            }

        # Step 3: Validate location
        try:
            is_inside, distance, location_log = GeolocationService.validate_location(
                user_lat=user_lat,
                user_lon=user_lon,
                log=True,
                ip_address=ip_address,
                user_agent=user_agent
            )

            if is_inside:
                # SUCCESS
                ValidationAttempt.objects.create(
                    qr_code=qr_code,
                    qr_hash_attempted=qr_hash,
                    user_latitude=user_lat,
                    user_longitude=user_lon,
                    distance_from_club=distance,
                    result=ValidationAttempt.ResultChoices.SUCCESS,
                    ip_address=ip_address,
                    user_agent=user_agent or '',
                    session_key=session_key or ''
                )

                return {
                    'success': True,
                    'qr_code': qr_code,
                    'distance': distance,
                    'result': 'success'
                }

            else:
                # LOCATION FAILED
                ValidationAttempt.objects.create(
                    qr_code=qr_code,
                    qr_hash_attempted=qr_hash,
                    user_latitude=user_lat,
                    user_longitude=user_lon,
                    distance_from_club=distance,
                    result=ValidationAttempt.ResultChoices.LOCATION_INVALID,
                    error_message=f"User is {distance:.0f}m from club location",
                    ip_address=ip_address,
                    user_agent=user_agent or '',
                    session_key=session_key or ''
                )

                return {
                    'success': False,
                    'error': f'You must be at the club to order. You are {distance:.0f}m away.',
                    'distance': distance,
                    'result': 'location_invalid'
                }

        except Exception as e:
            # LOCATION ERROR
            ValidationAttempt.objects.create(
                qr_code=qr_code,
                qr_hash_attempted=qr_hash,
                user_latitude=user_lat,
                user_longitude=user_lon,
                result=ValidationAttempt.ResultChoices.LOCATION_ERROR,
                error_message=f"Location validation error: {str(e)}",
                ip_address=ip_address,
                user_agent=user_agent or '',
                session_key=session_key or ''
            )

            return {
                'success': False,
                'error': 'Location validation failed',
                'result': 'location_error'
            }


# Backward compatibility class (legacy)
class BatchService:
    """Legacy service - use QRBatchService instead"""

    @staticmethod
    def create_batches():
        return QRBatchService.create_all_batches()

    @staticmethod
    def generate_qr_codes():
        return QRBatchService.generate_all_qr_codes()

    @staticmethod
    def toggle_batch():
        return QRBatch.close_current_and_activate_next()
