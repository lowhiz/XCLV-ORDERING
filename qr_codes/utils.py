import os
import qrcode
from django.core.files import File


def generate_qr_code_image(token, batch, folder_path):
    file_name = f"{token}.png"
    file_path = os.path.join(folder_path, file_name)
 
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    #Luigi, paki review nito kung ano dapat ang URL, like ano format. Thanks
    url = f"http://127.0.0.1:8000/order?token={token}"
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    
    return file_path, file_name