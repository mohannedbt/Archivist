import os

# your existing extractors
from app.extractors.pdf_extractor import Extract as extract_pdf
from app.extractors.image_extractor import Extract as extract_image
from app.extractors.text_extractor import getText as extract_docx


# -------------------------
# FILE TYPE DETECTION
# -------------------------
def detect_file_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext in [".pdf"]:
        return "pdf"

    if ext in [".png", ".jpg", ".jpeg", ".webp"]:
        return "image"

    if ext in [".docx"]:
        return "docx"


    return "unknown"


# -------------------------
# MAIN ROUTER
# -------------------------
def extract(filepath):
    file_type = detect_file_type(filepath)

    print(f"\n[ROUTER] File: {filepath}")
    print(f"[ROUTER] Detected type: {file_type}")

    try:
        # ---------------- PDF ----------------
        if file_type == "pdf":
            return extract_pdf(filepath)

        # ---------------- IMAGE ----------------
        if file_type == "image":
            return extract_image(filepath)

        # ---------------- DOCX ----------------
        if file_type == "docx":
            return extract_docx(filepath)


        # ---------------- UNKNOWN (SMART FALLBACK) ----------------
        print("[ROUTER] Unknown type → using PDF fallback first")

        try:
            return extract_pdf(filepath)
        except:
            pass

        try:
            return extract_image(filepath)
        except:
            pass

        return None

    except Exception as e:
        print(f"[ROUTER ERROR] {e}")
        return None
def GetSummary(filepath):
     pass
