import os

from app.extractors.pdf_extractor import Extract as pdf_extract
from app.extractors.image_extractor import Extract as image_extract
from app.extractors.text_extractor import getText as docx_extract


def detect_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return "pdf"
    if ext in [".png", ".jpg", ".jpeg"]:
        return "image"
    if ext == ".docx":
        return "docx"

    return "unknown"


def extract(filepath):
    t = detect_type(filepath)

    if t == "pdf":
        return pdf_extract(filepath)

    if t == "image":
        return image_extract(filepath)

    if t == "docx":
        return docx_extract(filepath)

    return ""