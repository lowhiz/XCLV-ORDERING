import os
import qrcode
from django.core.files import File


def generate_qr_code_image(token, qr_hash, batch, folder_path):
    """
    Generate QR code image with the proper URL

    Args:
        token: Human readable token (for filename)
        qr_hash: Hash to use in the URL
        batch: QR batch object
        folder_path: Where to save the image

    Returns:
        tuple: (file_path, file_name)
    """
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
    url = f"https://xclv-ordering.com/order?qr={qr_hash}"

    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

    return file_path, file_name
