import qrcode

# Your URL
url = "https://dorsa.mykaman.ir/utils/tickets/create/1"  # Replace with your desired URL

# Generate the QR code
qr = qrcode.QRCode(
    version=1,  # Controls the size of the QR Code (1 is the smallest)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
    box_size=10,  # Size of each box in the QR code
    border=4,  # Thickness of the border
)

qr.add_data(url)
qr.make(fit=True)

# Create an image from the QR code
img = qr.make_image(fill='black', back_color='white')

# Save the image
img.save("qr_code.png")
img.show()  # Optional: To show the QR code image
