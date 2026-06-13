from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

from app.services.ingestion_service import IngestionService
from app.core.event_bus import event_bus


# =========================
# EVENT TYPES
# =========================

FILE_CREATED = "file_created"
FILE_ERROR = "file_error"


# =========================
# HANDLER
# =========================

class FileCreatedHandler(FileSystemEventHandler):

    def __init__(self, ui_logger=None):
        self.ui_logger = ui_logger

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = str(event.src_path)
        filename = os.path.basename(filepath)

        try:
            # 1. process ingestion pipeline
            result = IngestionService.process(filepath)
            if self.ui_logger:
                self.ui_logger(f"NEW FILE: {filename}")
            # 2. emit success event
            event_bus.emit(FILE_CREATED, {
                "filepath": filepath,
                "filename": filename,
                "result": result
            })

        except Exception as e:
            # emit error event
            event_bus.emit(FILE_ERROR, {
                "filepath": filepath,
                "error": str(e)
            })


# =========================
# WATCHER
# =========================

class FileWatcher:

    def __init__(self, directory: str, ui_logger=None,on_file_moved=None):
        self.directory = directory
        self.observer = Observer()
        self.ui_logger = ui_logger
        self.on_file_moved = on_file_moved
        # subscribe to events so the UI can be updated when ingestion completes
        try:
            event_bus.subscribe(FILE_CREATED, self._on_created_event)
            event_bus.subscribe(FILE_ERROR, self._on_error_event)
        except Exception:
            # defensive: if event_bus not available at import time, ignore
            pass

    def watch_start(self):
        if not self.directory or not os.path.exists(self.directory):
            raise FileNotFoundError(f"Invalid watch directory: {self.directory}")

        handler = FileCreatedHandler(self.ui_logger)

        self.observer.schedule(
            handler,
            self.directory,
            recursive=True
        )

        self.observer.start()

        print(f"[WATCHER] Watching: {self.directory}")

        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()

    # -------------------------
    #  Event handlers
    # -------------------------
    def _on_created_event(self, data):
        # data expected: {"filepath": ..., "filename": ..., "result": record}
        if self.ui_logger:
            try:
                self.ui_logger(f"MOVED: {data.get('filename')}" )
            except Exception:
                pass

        if callable(self.on_file_moved):
            try:
                self.on_file_moved()
            except Exception:
                pass

    def _on_error_event(self, data):
        # data expected: {"filepath": ..., "error": ...}
        if self.ui_logger:
            try:
                self.ui_logger(f"ERROR: {data.get('filepath')} — {data.get('error')}")
            except Exception:
                pass