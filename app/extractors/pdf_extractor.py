import pymupdf4llm
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract


def _is_valid(text):
    return text is not None and text.strip() != ""


# -------------------------
# LEVEL 1: FAST MARKDOWN
# -------------------------
def extract_markdown(filepath):
    print(f"[LEVEL 1] pymupdf4llm → {filepath}")
    try:
        text = pymupdf4llm.to_markdown(filepath)

        if _is_valid(text):
            print("[LEVEL 1] SUCCESS (markdown extracted)")
            return text

        print("[LEVEL 1] EMPTY RESULT")

    except Exception as e:
        print(f"[LEVEL 1] ERROR: {e}")

    return None


# -------------------------
# LEVEL 2: PYPDF TEXT LAYER
# -------------------------
def extract_pypdf(filepath):
    print(f"[LEVEL 2] pypdf → {filepath}")
    try:
        reader = PdfReader(filepath)

        text = "\n".join((p.extract_text() or "") for p in reader.pages)

        if _is_valid(text):
            print("[LEVEL 2] SUCCESS (text layer extracted)")
            return text

        print("[LEVEL 2] EMPTY RESULT")

    except Exception as e:
        print(f"[LEVEL 2] ERROR: {e}")

    return None


# -------------------------
# LEVEL 3: PYMUPDF RAW TEXT
# -------------------------
def extract_pymupdf_raw(filepath):
    print(f"[LEVEL 3] pymupdf raw → {filepath}")
    try:
        import fitz
        doc = fitz.open(filepath)
        pages_text = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text()

            if text:
                pages_text.append(text)
            else:
                print(f"[LEVEL 3] Page {i} empty")

        text = "\n".join(pages_text)

        if _is_valid(text):
            print("[LEVEL 3] SUCCESS (raw text extracted)")
            return text

        print("[LEVEL 3] EMPTY RESULT")

    except Exception as e:
        print(f"[LEVEL 3] ERROR: {e}")

    return None


# -------------------------
# LEVEL 4: OCR
# -------------------------
def extract_ocr(filepath):
    print(f"[LEVEL 4] OCR → {filepath}")
    try:
        images = convert_from_path(filepath)

        print(f"[LEVEL 4] Pages to OCR: {len(images)}")

        text = []
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img)

            if page_text.strip():
                print(f"[LEVEL 4] Page {i} OCR success")
            else:
                print(f"[LEVEL 4] Page {i} empty OCR")

            text.append(page_text)

        final_text = "\n".join(text)

        if _is_valid(final_text):
            print("[LEVEL 4] SUCCESS (OCR extracted)")
            return final_text

        print("[LEVEL 4] EMPTY RESULT")

    except Exception as e:
        print(f"[LEVEL 4] ERROR: {e}")

    return ""


# -------------------------
# MASTER PIPELINE
# -------------------------
def Extract(filepath):
    print(f"\n========== EXTRACT START ==========")
    print(f"FILE: {filepath}")

    text = extract_markdown(filepath)
    if _is_valid(text):
        print("[PIPELINE] DONE at LEVEL 1\n")
        return text

    text = extract_pypdf(filepath)
    if _is_valid(text):
        print("[PIPELINE] DONE at LEVEL 2\n")
        return text

    text = extract_pymupdf_raw(filepath)
    if _is_valid(text):
        print("[PIPELINE] DONE at LEVEL 3\n")
        return text

    text = extract_ocr(filepath)

    print("[PIPELINE] DONE at LEVEL 4 (OCR fallback)\n")
    return text


