from pathlib import Path
from typing import List

from PIL import Image

from utils.pdf_handler import pdf_to_images


def load_images_from_file(path: str) -> List[Image.Image]:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return pdf_to_images(path)

    with Image.open(path) as img:
        return [img.convert("RGB")]
