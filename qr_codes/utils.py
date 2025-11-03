import os
import qrcode
from django.conf import settings
from django.core.files import File
from .models import QRCode, QRBatch  


def generate_qr_code_image(token, qr_hash, batch, folder_path):
    """
    Generate a QR code image file for a specific batch and token.

    Purpose:
    - Creates a QR code image that encodes a URL containing the qr_hash.
    - Saves the image to a folder for admin viewing, printing, or operational use.

    Steps:
    1. Determine the folder path where the QR image will be saved.
       - Defaults to MEDIA_ROOT/qrcodes/<batch_name> if not provided.
       - Ensures the folder exists (creates it if necessary).

    2. Generate the QR code:
       - Uses qrcode library with standard settings (version, error correction, box size, border).
       - Adds a URL with the qr_hash for scanning by customers.

    3. Save the image:
       - File name is based on the human-readable token.
       - Image is saved as a PNG in the specified folder.

    Args:
        token (str): Human-readable token, used for filename and identification.
        qr_hash (str): Secure hash to include in the URL.
        batch (QRBatch): The batch object the QR belongs to.
        folder_path (str): Directory to save the QR image.

    Returns:
        tuple: (file_path, file_name) of the saved image.
    """
    
    if folder_path is None:
        folder_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', batch.batch_name)

    os.makedirs(folder_path, exist_ok=True)
    file_name = f"{token}.png"
    file_path = os.path.join(folder_path, file_name)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Use the hash in the URL (not the token)
    # This is what customers will scan
    url = f"http://127.0.0.1:8000/order?qr={qr_hash}"

    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

    return file_path, file_name
