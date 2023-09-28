import os
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image

"""GENRATE QRCODE FOR PAYMENT"""


def payment_qrcode(approval_url, payment_id,logo_basewidth):
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(approval_url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
   
    
    logo = Image.open("payment/static/payment/images/Logo_.png")
    
    
    # adjust image size
    wpercent = (logo_basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((logo_basewidth, hsize), Image.Resampling.LANCZOS)
   
    
    # set size of QR code
    pos = ((qr_image.size[0] - logo.size[0]) // 2,
        (qr_image.size[1] - logo.size[1]) // 2)
    qr_image.paste(logo, pos)
    

    # Save the QR code image to a BytesIO buffer
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Construct the path to the 'qrcodes' directory
    qrcodes_dir = os.path.join(settings.MEDIA_ROOT, "qrcodes")

    # Save the image to the 'qrcodes' directory in your media root
    fs = FileSystemStorage(location=qrcodes_dir)
    filename = f"{payment_id}/qrcode.png"
    filepath = fs.save(filename, qr_buffer)

    # Get the URL of the saved QR code image
    qr_image_url = os.path.join(settings.MEDIA_URL, "qrcodes", filename)

    return {"qr_image_url": f"http://127.0.0.1:8000{qr_image_url}"}
