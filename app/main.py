import os
import threading
import argparse

from app.database.db import Database
from app.models.file_record import FileRecord
from app.models.settings import Settings
from app.config.setting_manager import SettingsManager
from app.watcher.file_watcher import FileWatcher
from app.ui.dashboard import run_ui


# =========================
# CORE INIT (shared)
# =========================

def init_system():
    db_path = SettingsManager.DEFAULTS["database_url"]

    Database.init(db_path)
    Database.connect()
    Database.create_tables([FileRecord, Settings])

    SettingsManager.init_defaults()

    print("[SYSTEM] Initialized")


# =========================
# WATCHER MODE
# =========================

def run_watcher():
    path = os.path.expanduser("~/Downloads")

    watcher = FileWatcher(path)
    watcher.watch_start()


# =========================
# CLI ENTRY
# =========================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ui", action="store_true", help="Run UI dashboard")
    parser.add_argument("--watch", action="store_true", help="Run watcher only")

    args = parser.parse_args()

    init_system()

    # -------------------------
    # UI MODE
    # -------------------------
    if args.ui:
        print("[SYSTEM] Starting UI mode")
        run_ui()

    # -------------------------
    # WATCH MODE (HEADLESS)
    # -------------------------
    elif args.watch:
        print("[SYSTEM] Starting watcher mode")
        run_watcher()

    # -------------------------
    # DEFAULT MODE (BOTH)
    # -------------------------
    else:
        print("[SYSTEM] Starting default mode (UI + watcher)")

        t = threading.Thread(target=run_watcher, daemon=True)
        t.start()

        run_ui()