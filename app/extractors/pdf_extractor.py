import fitz
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

from pypdf import PdfReader


# =========================
# TYPE SAFETY NORMALIZER
# =========================

def normalize_text(text):
    """
    Ensures output is always a clean string.
    Handles:
    - str
    - list[str]
    - None
    """

    if text is None:
        return ""

    if isinstance(text, list):
        return "\n".join(str(x) for x in text)

    return str(text)


def _is_valid(text):
    text = normalize_text(text)
    return len(text.strip()) > 0


# =========================
# PDF TYPE CLASSIFIER
# =========================

class PDFType:
    DIGITAL = "digital"
    SCANNED = "scanned"
    MIXED = "mixed"


def classify_pdf(filepath: str):
    """
    Detect PDF type based on text density.
    """

    doc = fitz.open(filepath)

    total_pages = len(doc)
    text_pages = 0

    for i in range(total_pages):
        page = doc.load_page(i)
        text = normalize_text(page.get_text())

        if len(text.strip()) > 50:
            text_pages += 1

    ratio = text_pages / total_pages if total_pages else 0

    if ratio > 0.7:
        return PDFType.DIGITAL

    if ratio < 0.2:
        return PDFType.SCANNED

    return PDFType.MIXED


# =========================
# LEVEL 1: MARKDOWN
# =========================

def extract_markdown(filepath):
    print(f"[LEVEL 1] markdown → {filepath}")

    try:
        import pymupdf4llm
        text = pymupdf4llm.to_markdown(filepath)

        text = normalize_text(text)

        if _is_valid(text):
            return text

    except Exception as e:
        print(f"[LEVEL 1 ERROR] {e}")

    return None


# =========================
# LEVEL 2: PYPDF
# =========================

def extract_pypdf(filepath):
    print(f"[LEVEL 2] pypdf → {filepath}")

    try:
        reader = PdfReader(filepath)

        pages = []
        for p in reader.pages:
            pages.append(normalize_text(p.extract_text()))

        text = "\n".join(pages)

        if _is_valid(text):
            return text

    except Exception as e:
        print(f"[LEVEL 2 ERROR] {e}")

    return None


# =========================
# LEVEL 3: HYBRID (SMART OCR)
# =========================

def extract_hybrid_pymupdf(filepath):
    """
    Per-page smart extraction:
    - text first
    - OCR only if needed
    """

    print(f"[HYBRID] pymupdf → {filepath}")

    try:
        doc = fitz.open(filepath)

        pages_text = []

        for i in range(len(doc)):
            page = doc.load_page(i)

            # 1. Try digital text
            text = normalize_text(page.get_text())

            if len(text.strip()) > 20:
                pages_text.append(text)
                continue

            # 2. OCR fallback
            print(f"[PAGE {i}] OCR fallback")

            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")

            image = Image.open(io.BytesIO(img_bytes))
            ocr_text = pytesseract.image_to_string(image)

            pages_text.append(normalize_text(ocr_text))

        final_text = "\n".join(pages_text)

        if _is_valid(final_text):
            return final_text

    except Exception as e:
        print(f"[HYBRID ERROR] {e}")

    return None


# =========================
# MASTER PIPELINE
# =========================

def Extract(filepath):
    print("\n========== PDF EXTRACT START ==========")
    print(f"FILE: {filepath}")

    pdf_type = classify_pdf(filepath)
    print(f"[PDF TYPE] {pdf_type}")

    # -------------------------
    # DIGITAL
    # -------------------------
    if pdf_type == PDFType.DIGITAL:

        text = extract_markdown(filepath)
        if _is_valid(text):
            print("[DONE] markdown")
            return text

        text = extract_pypdf(filepath)
        if _is_valid(text):
            print("[DONE] pypdf")
            return text

        return extract_hybrid_pymupdf(filepath)

    # -------------------------
    # SCANNED
    # -------------------------
    if pdf_type == PDFType.SCANNED:
        return extract_hybrid_pymupdf(filepath)

    # -------------------------
    # MIXED
    # -------------------------
    if pdf_type == PDFType.MIXED:

        text = extract_pypdf(filepath)
        if _is_valid(text):
            print("[DONE] mixed → pypdf")
            return text

        return extract_hybrid_pymupdf(filepath)

    return ""