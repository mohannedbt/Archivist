import os
import shutil
import hashlib
import datetime

from app.extractors.router import extract
from app.classifiers.rule_classifier import Categorize


def convert(epoch):
    return datetime.datetime.fromtimestamp(epoch)


def calculate_hash(filepath):
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_file_info(filepath):
    stats = os.stat(filepath)

    text = extract(filepath)
    category = Categorize(str(text or ""))

    return {
        "path": filepath,
        "filename": os.path.basename(filepath),
        "created_at": convert(stats.st_ctime),
        "file_hash": calculate_hash(filepath),
        "summary": (text or "")[:300],
        "category": category,
    }


def ensure_directory(path):
    os.makedirs(path, exist_ok=True)


def move_file(filepath, target_dir):
    ensure_directory(target_dir)

    filename = os.path.basename(filepath)
    destination = os.path.join(target_dir, filename)

    base, ext = os.path.splitext(filename)
    i = 1

    while os.path.exists(destination):
        destination = os.path.join(target_dir, f"{base}_{i}{ext}")
        i += 1

    shutil.move(filepath, destination)
    return destination