# Archivist

Archivist is an AI-assisted, local file organizer that watches incoming files (for example your Downloads folder), extracts content, classifies files, stores structured metadata, and moves files into an organized folder hierarchy.

This repository contains a v1 implementation with a GUI (Tkinter), a filesystem watcher, extractors for common file types, a small rule-based classifier, and a simple SQLite-backed metadata store.

--

## Goals

- Automatically process new files arriving in a watch folder.
- Extract text and metadata from files (PDF, images, text, ...).
- Categorize files and move them into organized folders.
- Keep a searchable metadata record of processed files.
- Provide a simple UI for configuration and monitoring.

This project is intentionally minimal and modular so we can swap in smarter components (embeddings, LLMs, RAG search) in later phases.

--

## Quick Start

Prerequisites: Python 3.10+ and the project `requirements.txt` installed in a virtual environment.

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Run the app (default mode: UI + watcher):

```bash
python3 -m app.main
```

3. The UI lets you choose a `Downloads` folder and an `Organized` folder, and start the watcher. Drop or copy files into the watched folder to exercise the pipeline.

--

## What the app does (high-level)

1. `FileWatcher` monitors a directory and emits file-created events.
2. `IngestionService` runs the pipeline for a new file:
   - Extract content using the appropriate extractor (PDF, image OCR, text, ...).
   - Classify the file (v1: rule-based classifier in `app/classifiers/rule_classifier.py`).
   - Save a `FileRecord` entry into the SQLite DB (`data/archivist.db`).
   - Move the file into `organized/<category>` (creates subfolders as needed).
3. The UI (`app/ui/dashboard.py`) displays status, logs, counters, and lets you start/stop the watcher.
4. A lightweight `EventBus` decouples components — the watcher, ingestion service and UI communicate via events.

--

## Important Files and Responsibilities

- `app/main.py` — application entry point, initializes DB, settings and starts the app.
- `app/config/setting_manager.py` — settings helpers; `init_defaults()` populates default settings in DB.
- `app/watcher/file_watcher.py` — uses `watchdog` to detect new files and trigger ingestion.
- `app/services/ingestion_service.py` — orchestrates processing and calls `move_file()`.
- `app/helper/FileHelper.py` — helpers: extraction routing (`extract()`), file hashing and movement logic.
- `app/extractors/` — per-file-type extractors (PDF, image, text). They return text and metadata used by the classifier.
- `app/classifiers/rule_classifier.py` — categorizes files using simple rules. Replaceable with embeddings/LLMs later.
- `app/models/` — database models (`FileRecord`, `Settings`).
- `app/ui/dashboard.py` — Tkinter-based dashboard; shows stats and logs.

When changing behavior, prefer changing the service and helper modules (not UI) so core logic remains testable.

--

## Settings

Settings are stored in the `settings` table in the SQLite DB. The `SettingsManager` exposes helper methods:

- `SettingsManager.init_defaults()` — create default rows for keys that are missing.
- `SettingsManager.get(key, default=None)` — return stored value or default.
- `SettingsManager.set(key, value)` — update or create setting.

Key defaults (see `app/config/setting_manager.py`):

- `downloads_dir` — default: `~/Downloads`
- `organized_dir` — default: `data/organized`
- `database_url` — default: `data/archivist.db`
- `allowed_extensions` — default: `.pdf,.txt,.jpg,.png`

If a stored setting points to an invalid path (for example a Windows path on Linux), the watcher will raise a `FileNotFoundError` when trying to start. To fix: update the `downloads_dir` in the DB or via the UI.

--

## Running and Testing the Pipeline

To manually test the pipeline without the UI:

1. Ensure DB exists and defaults are initialised:

```bash
python3 -c "from app.database.db import Database; from app.config.setting_manager import SettingsManager; Database.init('data/archivist.db'); Database.connect(); SettingsManager.init_defaults(); print('db ready')"
```

2. Trigger ingestion programmatically (small example):

```bash
python3 - <<'PY'
from app.services.ingestion_service import IngestionService
IngestionService.process('/path/to/test.pdf')
print('done')
PY
```

3. Or start the watcher and drop a file in the watched folder to see logs and DB entries.

--

## Debugging tips

- If the watcher prints a `FileNotFoundError: Invalid watch directory: ...`, check the stored `downloads_dir` value in the DB. You can update it via `SettingsManager.set()` or delete the record so `init_defaults()` repopulates defaults.
- Duplicate logs like multiple "Watching: /some/path" indicate multiple watcher instances; ensure you only run a single UI/daemon.
- If files are not moved but ingestion prints `[INGESTED]`, verify `move_file()` in `app/helper/FileHelper.py` and check filesystem permissions of the target folder.

--

## Architecture Details (components)

- EventBus (`app/core/event_bus.py`) — in-memory pub/sub. Events used:
  - `FILE_CREATED` — emitted by the watcher after successful ingestion.
  - `FILE_ERROR` — emitted on errors.
- Watcher (`app/watcher/file_watcher.py`) — schedules a `FileCreatedHandler` that runs ingestion and emits events. The dashboard subscribes to events and updates counters.
- Ingestion (`app/services/ingestion_service.py`) — de-duplicates by file path, extracts text, classifies, saves `FileRecord` and moves the file.
- Extractors (`app/extractors/*`) — return text for classification and summaries for metadata.

--

## Roadmap — Next Steps (high detail)

The following is a prioritized roadmap with acceptance criteria and action items for each feature. Each item is broken down into smaller tasks and measurable milestones.

1) AI File Brain — core research & design
   - Goal: Replace or augment rule-based classification with an AI-driven system that understands content semantics.
   - Tasks:
     - Evaluate local inference vs cloud LLMs constraints (privacy, latency, cost).
     - Choose embedding model (local/on-device) for semantic similarity (e.g. sentence-transformers) or use OpenAI embeddings if cloud allowed.
     - Design metadata schema changes: store embeddings in DB or a separate vector store.
     - Acceptance: same-file classification accuracy improves vs rule baseline on held-out sample.

2) Auto Categories UI panel
   - Goal: Show suggested categories with confidence, allow user to override and save corrections.
   - Tasks:
     - Add a UI panel in `app/ui/dashboard.py` listing recent ingested files with category suggestions and a dropdown for user selection.
     - Persist corrections to `FileRecord.category` and record `user_corrected` flag.
     - Acceptance: UI displays suggestions and corrected categories persist to DB.

3) Smart Summaries preview
   - Goal: Provide concise, context-aware summaries for files (first-class metadata in `FileRecord.summary`).
   - Tasks:
     - Implement a summarizer glue that can use either a small local LLM (e.g. Llama.cpp) or heuristic summarizer fallback.
     - Add UI preview and optional “Regenerate summary” action.
     - Acceptance: Summaries are saved and visible in UI; optional compare between 2 summarizers.

4) Drag & Drop organizer
   - Goal: Allow users to drag entries in the UI to change categories or target folders, and have the organizer move files accordingly.
   - Tasks:
     - Add drag/drop UX in the UI listing and implement a programmatic move API in `Organizer`.
     - Ensure move operations update database and emit events for counters.
     - Acceptance: Dragging an item moves the file on disk and updates the DB entry.

5) Duplicate detection system
   - Goal: Detect identical (or near-duplicate) files via hash + fuzzy similarity and provide merge/keep options.
   - Tasks:
     - File hashing already exists (`calculate_hash`); extend DB schema to index `file_hash`.
     - Implement fuzzy similarity by small embedding compare + edit-distance for text.
     - Provide a conflict resolution UI (keep newest, keep largest, keep both with renaming).
     - Acceptance: Duplicates detected and user can resolve them from UI.

6) Semantic file search (RAG-ready)
   - Goal: Allow semantic queries over your files ("find meeting notes about project X") using embeddings + optional RAG recall.
   - Tasks:
     - Add embeddings pipeline for each `FileRecord` summary/content.
     - Integrate a vector store (SQLite+FAISS or external) or store embeddings in DB if small.
     - Implement search endpoint and a small UI to run semantic queries and show results ranked by similarity.
     - Acceptance: Search returns relevant files for human-verified prompts.

--

## Next Plan — Implementation Phases (concrete)

Phase A — Stabilize & UX (1–2 weeks)
- Harden settings flow: ensure `SettingsManager.init_defaults()` runs before UI reads defaults; validate settings and show warnings.
- Add a small searchable recent-file list in the UI and wire event bus updates.
- Add tests for `move_file`, `calculate_hash`, and ingestion dedup path.

Phase B — AI File Brain PoC (2–3 weeks)
- Build a prototype pipeline producing embeddings for documents and run a simple KNN-retrieval.
- Replace rule classifier with a “suggestion” step that uses KNN+rules hybrid.

Phase C — Interaction features (2–4 weeks)
- Implement Auto Categories panel, Smart Summaries preview, and Drag & Drop organizer.
- Add duplication detection UI and resolution flows.

Phase D — Semantic Search & RAG (3–6 weeks)
- Build vector store persistence, advanced query UI, and optional RAG answer UI that composes file content.

--

## Milestones & Acceptance Criteria

- M1: Stable watcher + UI that displays defaults and counters (current state). Tests for ingestion flow.
- M2: Auto Categories UI + persistent corrections and improved classification suggestions.
- M3: Duplicate detection and resolve UI.
- M4: Semantic search with embeddings and satisfactory precision on sample queries.

--

## Development notes and conventions

- Keep core logic in `app/services` and `app/helper` so it is testable without the UI.
- Use the `EventBus` for cross-component notifications — UI subscribes to `FILE_CREATED` and `FILE_ERROR`.
- Store human corrections and metadata in `FileRecord` for future learning.

--

## Contributing

1. Create a feature branch `feature/<short-description>`.
2. Run linters and tests locally.
3. Open a PR with a short description and testing notes.

--

## Contact

Open issues in the repo for feature requests, bugs, or architecture changes.

--

Thank you — Archivist is deliberately small and modular so you can iterate quickly. The next big upgrade is the "AI File Brain": embeddings, suggestions, and a semantic UX. See "Roadmap — Next Steps" above for full details.
