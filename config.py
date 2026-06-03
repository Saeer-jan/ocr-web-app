import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "bmp", "tiff", "webp"}

    DEFAULT_LANG = os.getenv("OCR_DEFAULT_LANG", "en")
    SUPPORTED_LANGS = [lang.strip() for lang in os.getenv("OCR_SUPPORTED_LANGS", "en,fr,de,es,ch,ar,hi").split(",") if lang.strip()]

    ENABLE_TABLE_DETECTION = os.getenv("OCR_ENABLE_TABLE_DETECTION", "true").lower() == "true"
    ENABLE_HANDWRITING = os.getenv("OCR_ENABLE_HANDWRITING", "true").lower() == "true"
