import os
import qrcode
from PIL import Image # Needed for image handling for putting logo in the center of the QR code
from django.conf import settings
from django.core.files import File
from .models import QRCode, QRBatch


def generate_qr_code_image(token, qr_hash, batch, folder_path):
    """
    Generate a QR code image file for a specific batch and token with a center logo.

    Purpose:
    - Creates a QR code image that encodes a URL containing the qr_hash.
    - Adds a center logo image to the QR code.
    - Saves the image to a folder for admin viewing, printing, or operational use.

    Steps:
    1. Determine the folder path where the QR image will be saved.
       - Defaults to MEDIA_ROOT/qrcodes/<batch_name> if not provided.
       - Ensures the folder exists (creates it if necessary).

    2. Generate the QR code:
       - Uses qrcode library with HIGH error correction to allow for center logo.
       - Adds a URL with the qr_hash for scanning by customers.

    3. Add center logo:
       - Opens the logo image from static/images/xclv-square.png
       - Resizes it proportionally to fit in the QR code center
       - Pastes it onto the QR code

    4. Save the image:
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

    # Use HIGH error correction to allow for center logo overlay
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Changed to HIGH
        box_size=10,
        border=4,
    )

    # Use the hash in the URL (not the token)
    # This is what customers will scan

    # Original implementation is as follows:
    ## url = f"http://127.0.0.1:8000/order?qr={qr_hash}"
    # This works for now, but in production the URL depends on deployment
    # We use settings.py of the Django project to get the base URL

    base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
    url = f"{base_url}/order?qr={qr_hash}"

    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB') # Convert to RGB for logo overlay

    # Add center logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'xclv-square.png')

    try:
        logo = Image.open(logo_path)

        # Calculate logo size (10-15% of QR code size works well)
        qr_width, qr_height = img.size
        logo_size = min(qr_width, qr_height) // 5  # 20% of QR code size

        # Resize logo while maintaining aspect ratio
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

        # Calculate position to center the logo
        logo_width, logo_height = logo.size
        logo_position = (
            (qr_width - logo_width) // 2,
            (qr_height - logo_height) // 2
        )

        # Paste logo onto QR code
        # If logo has transparency, use it as mask
        if logo.mode == 'RGBA':
            img.paste(logo, logo_position, logo)
        else:
            img.paste(logo, logo_position)

    except FileNotFoundError:
        print(f"Warning: Logo file not found at {logo_path}. Generating QR code without logo.")
    except Exception as e:
        print(f"Warning: Could not add logo to QR code: {e}. Generating QR code without logo.")

    img.save(file_path)

    return file_path, file_name
