# Archivist V1

AI-powered download intelligence system that watches incoming files, understands their content, classifies them, stores metadata, and organizes them automatically.

---

# Goal

Transform:

```text
Downloads/
├── paper.pdf
├── CV_final_v3.pdf
├── screenshot.png
└── project.zip
```

Into:

```text
Organized/
├── Learning/
├── Projects/
├── Internships/
└── Personal/
```

without relying entirely on hardcoded rules.

---

# System Architecture

```text
File Appears
      ↓
Watcher
      ↓
Ingestion Service
      ↓
Analyzer
      ↓
Extractor
      ↓
Classifier
      ↓
Database
      ↓
Organizer
```

---

# Folder Structure

```text
app/
├── main.py
├── config/
├── models/
├── database/
├── watcher/
├── extractors/
├── classifiers/
├── organizers/
└── services/
```

---

# File Responsibilities

---

## app/main.py

### Purpose

Application entry point.

This file starts Archivist.

Responsibilities:

* Load configuration
* Initialize database
* Start watcher
* Register services

Example flow:

```text
Start App
   ↓
Connect Database
   ↓
Start File Watcher
   ↓
Wait For Events
```

Think of this as the engine start button.

---

## app/config/settings.py

### Purpose

Centralized configuration.

Store:

* Downloads folder path
* Organized folder path
* Database path
* Allowed file types
* Logging settings

Example:

```text
Downloads Directory
Processing Directory
Categories
```

Avoid hardcoding paths elsewhere.

---

## app/models/file_record.py

### Purpose

Represents a file inside the system.

Defines the structure of stored metadata.

Example information:

```text
filename
path
category
summary
hash
created_at
```

This becomes the source of truth for processed files.

---

## app/database/db.py

### Purpose

Database initialization.

Responsibilities:

* Create database connection
* Create tables
* Initialize schema

This file knows how to create the database.

---

## app/database/session.py

### Purpose

Database session management.

Responsibilities:

* Open database sessions
* Close sessions
* Handle transactions

Other services should request sessions from here.

---

## app/watcher/file_watcher.py

### Purpose

Monitors folders for changes.

Responsibilities:

* Detect new files
* Detect updates
* Trigger ingestion pipeline

Example:

```text
New file:
OperatingSystems.pdf
```

The watcher does not understand files.

It only notices that something happened.

---

## app/services/ingestion_service.py

### Purpose

Orchestrates processing.

This is the most important service.

Responsibilities:

1. Receive new file
2. Analyze metadata
3. Extract content
4. Classify
5. Save results
6. Organize file

Think of it as the conductor of the orchestra.

---

## app/extractors/

### Purpose

Convert files into text and metadata.

Different file types require different extractors.

---

### pdf_extractor.py

Responsibilities:

* Read PDF content
* Extract title
* Extract text
* Count pages

Output:

```text
PDF Content
Metadata
```

---

### text_extractor.py

Responsibilities:

* Read txt files
* Read markdown files
* Extract content

Output:

```text
Raw Text
```

---

### image_extractor.py

Responsibilities:

* OCR screenshots
* OCR scanned documents
* Extract visible text

Output:

```text
Detected Text
```

---

# Future Extractors

Potential additions:

```text
zip_extractor.py
audio_extractor.py
video_extractor.py
repo_extractor.py
```

---

## app/classifiers/rule_classifier.py

### Purpose

Determine file category.

Input:

```text
Extracted Content
```

Output:

```text
Learning
Projects
Internships
Personal
Other
```

V1 uses rules.

Future versions may use:

* Embeddings
* Local LLMs
* Fine-tuned models

---

## app/organizers/organizer.py

### Purpose

Move files to final destinations.

Responsibilities:

* Create folders
* Move files
* Rename files
* Archive files

Input:

```text
Category
Original File
```

Output:

```text
Moved File
```

This is the component that changes the filesystem.

---

# Data Folder

```text
data/
├── raw/
├── processed/
└── archivist.db
```

---

## data/raw/

Purpose:

Temporary processing area.

Files may be copied here before analysis.

Useful for debugging.

---

## data/processed/

Purpose:

Stores processed artifacts.

Examples:

```text
Summaries
Extracted Text
Metadata
```

Useful for future AI training and evaluation.

---

## data/archivist.db

Purpose:

SQLite database.

Stores:

* Processed files
* Categories
* Summaries
* Hashes
* Metadata

---

# Tests Folder

```text
tests/
```

Purpose:

Verify behavior.

Example tests:

```text
PDF extraction works
Classifier returns expected category
Organizer moves files correctly
```

---

# Scripts Folder

```text
scripts/
```

Purpose:

Utility scripts.

Examples:

```text
Create folders
Reset database
Import sample files
```

Not part of production runtime.

---

# Docs Folder

```text
docs/
```

Purpose:

Architecture and design documents.

Possible documents:

```text
system_design.md
roadmap.md
future_features.md
```

---

# V1 Categories

Initial categories:

```text
Learning
Projects
Internships
Personal
Media
Other
```

Keep this intentionally simple.

---

# V1 Success Criteria

Archivist V1 is considered complete when:

1. Watcher detects new files.
2. Extractor reads file content.
3. Classifier determines category.
4. Metadata is saved.
5. Organizer moves the file.
6. Processing history is visible in SQLite.

At this point the complete ingestion pipeline exists and future AI improvements can be added without redesigning the architecture.
