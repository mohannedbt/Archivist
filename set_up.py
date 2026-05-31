from pathlib import Path

ROOT = Path("../Archivist")

directories = [
    "app",
    "app/config",
    "app/models",
    "app/database",
    "app/watcher",
    "app/extractors",
    "app/classifiers",
    "app/organizers",
    "app/services",
    "data",
    "data/raw",
    "data/processed",
    "tests",
    "scripts",
    "docs",
]

files = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "app/main.py",
    "app/config/settings.py",
    "app/models/file_record.py",
    "app/database/db.py",
    "app/database/session.py",
    "app/watcher/file_watcher.py",
    "app/extractors/pdf_extractor.py",
    "app/extractors/text_extractor.py",
    "app/extractors/image_extractor.py",
    "app/classifiers/rule_classifier.py",
    "app/organizers/organizer.py",
    "app/services/ingestion_service.py",
]

print("Creating Archivist project structure...")

ROOT.mkdir(exist_ok=True)

for directory in directories:
    path = ROOT / directory
    path.mkdir(parents=True, exist_ok=True)
    print(f"[DIR ] {path}")

for file in files:
    path = ROOT / file

    if not path.exists():
        path.touch()
        print(f"[FILE] {path}")

print("\nArchivist structure created successfully.")