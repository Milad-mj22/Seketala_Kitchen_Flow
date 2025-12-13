import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path

# ======================
# Settings
# ======================
url = "https://dorsa.mykaman.ir/utils/tickets/create/1"
project_name = "سنس اسیدشویی"
output_file = f"qr_code_{project_name}.png"

BORDER_SIZE = 2
BORDER_COLOR = "black"

# مسیر فونت
BASE_DIR = Path(
    r'C:\Users\Dorsa-Co\Desktop\GitlabRepoes\Seketala_Kitchen_Flow\users\static\fonts'
).resolve().parent
font_path = BASE_DIR / "fonts" / "Vazirmatn-Bold.woff2"

# ======================
# Generate QR Code
# ======================
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)
qr_img = qr.make_image(
    fill_color="black",
    back_color="white"
).convert("RGB")

# ======================
# Prepare Persian Text (RTL)
# ======================
reshaped_text = arabic_reshaper.reshape(project_name)
bidi_text = get_display(reshaped_text)

# ======================
# Load Font (with fallback)
# ======================
font = None

if font_path.exists():
    font = ImageFont.truetype(str(font_path), 40)
else:
    windows_font_candidates = [
        r"C:\Windows\Fonts\Vazirmatn-Regular.ttf",
        r"C:\Windows\Fonts\Tahoma.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguiemj.ttf",
    ]
    for fp in windows_font_candidates:
        if Path(fp).exists():
            font = ImageFont.truetype(fp, 40)
            break

if font is None:
    raise FileNotFoundError(
        f"فونت پیدا نشد.\n"
        f"مسیر مورد انتظار: {font_path}"
    )

# ======================
# Draw Text (no gap)
# ======================
draw = ImageDraw.Draw(qr_img)
bbox = draw.textbbox((0, 0), bidi_text, font=font)

text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_top_offset = bbox[1]

final_img = Image.new(
    "RGB",
    (qr_img.width, qr_img.height + text_height),
    "white"
)

final_img.paste(qr_img, (0, 0))

draw = ImageDraw.Draw(final_img)
text_x = (final_img.width - text_width) // 2
text_y = qr_img.height - text_top_offset

draw.text(
    (text_x, text_y),
    bidi_text,
    fill="black",
    font=font
)

# ======================
# Add Border
# ======================
final_img = ImageOps.expand(
    final_img,
    border=BORDER_SIZE,
    fill=BORDER_COLOR
)

# ======================
# Save & Show
# ======================
final_img.save(output_file)
final_img.show()

print("Saved:", output_file)
