import easyocr
import re

def clean_easyocr_result(result, min_conf=0.6):
    cleaned = []

    for bbox, text, conf in result:

        # confidence filter
        if conf < min_conf:
            continue

        text = text.strip()

        # remove junk
        if len(text) < 2:
            continue

        # remove pure symbols/numbers noise
        if re.fullmatch(r"[\W_0-9]+", text):
            continue

        cleaned.append(text)

    return " ".join(cleaned)
def Extract(filepath):
  reader = easyocr.Reader(['fr','en'],gpu=False) # this needs to run only once to load the model into memory
  result = reader.readtext(filepath)
  clean  = clean_easyocr_result(result)
  return clean
