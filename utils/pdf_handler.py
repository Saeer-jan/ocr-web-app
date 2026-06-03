from typing import List

from PIL import Image


def pdf_to_images(path: str) -> List[Image.Image]:
    try:
        from pdf2image import convert_from_path

        return convert_from_path(path)
    except Exception:
        return []
