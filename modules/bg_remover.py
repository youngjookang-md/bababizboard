from PIL import Image
import io

def remove_background(image: Image.Image) -> Image.Image:
    from rembg import remove
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    result_bytes = remove(img_bytes.read())
    return Image.open(io.BytesIO(result_bytes)).convert("RGBA")
