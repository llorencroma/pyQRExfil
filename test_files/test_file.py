import qrcode
import random

# Generate a random string of 10 digits
random_str = ''.join(random.choices('0123456789', k=10))

# Generate a QR code for the random string
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(random_str)
qr.make(fit=True)

# Create an image from the QR code
img = qr.make_image(fill_color="black", back_color="white")

# Save the image as a PNG file
img.save(f"qrcode_{random_str}.png")


