import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os

from app.database.db import Database
from app.models.file_record import FileRecord
from app.models.settings import Settings
from app.config.setting_manager import SettingsManager
from app.watcher.file_watcher import FileWatcher


# ─────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────

BG        = "#0f172a"   # page / outer bg
SURFACE   = "#1e293b"   # card bg
SURFACE2  = "#0d1424"   # log / inner bg
BORDER    = "#334155"   # subtle borders
ACCENT    = "#38bdf8"   # cyan – primary action
ACCENT_BG = "#0c4a6e"   # tinted accent bg
DANGER    = "#f87171"   # stop / error text
DANGER_BG = "#3b0f0f"   # tinted danger bg
SUCCESS   = "#4ade80"
WARNING   = "#fbbf24"
INFO      = "#7dd3fc"
TEXT      = "#f1f5f9"   # primary text
MUTED     = "#94a3b8"   # secondary text
HINT      = "#475569"   # timestamps / labels

F         = ("Segoe UI", 10)
F_SM      = ("Segoe UI", 9)
F_MONO    = ("Consolas", 9)
F_BOLD    = ("Segoe UI", 10, "bold")
F_TITLE   = ("Segoe UI", 15, "bold")
F_LABEL   = ("Segoe UI", 8)
F_BIG     = ("Segoe UI", 20, "bold")


def _ts():
    return time.strftime("%H:%M:%S")


# ─────────────────────────────────────────
#  REUSABLE WIDGETS
# ─────────────────────────────────────────

class StatCard(tk.Frame):
    """Metric card: small muted label + large bold value."""

    def __init__(self, parent, label, **kw):
        super().__init__(parent, bg=SURFACE, padx=14, pady=10, **kw)
        tk.Label(self, text=label.upper(), bg=SURFACE, fg=HINT,
                 font=("Segoe UI", 7, "bold")).pack(anchor="w")
        self._var = tk.StringVar(value="—")
        tk.Label(self, textvariable=self._var, bg=SURFACE, fg=TEXT,
                 font=F_BIG).pack(anchor="w", pady=(2, 0))

    def set(self, v):
        self._var.set(str(v))


class Divider(tk.Frame):
    """1-px horizontal rule."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BORDER, height=1, **kw)
        self.pack(fill="x", pady=5)


class PathRow(tk.Frame):
    """One path config row: icon · name/value · Choose button."""

    def __init__(self, parent, label, icon, on_pick, **kw):
        super().__init__(parent, bg=SURFACE, pady=6, **kw)

        # icon pill
        tk.Label(self, text=icon, bg=ACCENT_BG, fg=ACCENT,
                 font=("Segoe UI", 11), width=3,
                 pady=3).pack(side="left", padx=(0, 10))

        # text
        tf = tk.Frame(self, bg=SURFACE)
        tf.pack(side="left", fill="x", expand=True)
        tk.Label(tf, text=label, bg=SURFACE, fg=TEXT,
                 font=F, anchor="w").pack(fill="x")
        self._var = tk.StringVar(value="Not selected")
        tk.Label(tf, textvariable=self._var, bg=SURFACE, fg=MUTED,
                 font=F_SM, anchor="w").pack(fill="x")

        # button
        self._btn = tk.Button(
            self, text="Choose", command=on_pick,
            bg=SURFACE, fg=MUTED, relief="flat", bd=0, font=F_SM,
            activebackground=BORDER, activeforeground=TEXT,
            cursor="hand2", padx=10, pady=4,
            highlightthickness=1, highlightbackground=BORDER,
        )
        self._btn.pack(side="right")

    def set(self, path: str):
        self._var.set(path)

    def get(self) -> str:
        v = self._var.get()
        return v if v != "Not selected" else ""


class IconButton(tk.Button):
    """Flat button with consistent styling."""

    def __init__(self, parent, text, bg, fg, active_bg, active_fg, **kw):
        super().__init__(
            parent, text=text,
            bg=bg, fg=fg,
            activebackground=active_bg, activeforeground=active_fg,
            relief="flat", bd=0, font=F_BOLD,
            cursor="hand2", padx=18, pady=9,
            **kw,
        )


# ─────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────

class ArchivistUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Archivist")
        self.root.geometry("740x620")
        self.root.minsize(640, 520)
        self.root.configure(bg=BG)

        self.watcher: FileWatcher | None = None
        self.watcher_thread: threading.Thread | None = None
        self._running        = False
        self._start_time     = 0.0
        self._uptime_job     = None
        self._files_moved    = 0
        self._event_count    = 0

        self._build()

    # ──────────────────────────────────────
    #  BUILD
    # ──────────────────────────────────────

    def _build(self):
        self._build_header()
        self._build_stats()
        self._build_paths()
        self._build_actions()
        self._build_log()

    # ── header ──────────────────────────

    def _build_header(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 6))

        # logo + title
        logo = tk.Frame(bar, bg=ACCENT_BG, padx=10, pady=6)
        logo.pack(side="left")
        tk.Label(logo, text="⬡", bg=ACCENT_BG, fg=ACCENT,
                 font=("Segoe UI", 14)).pack()

        info = tk.Frame(bar, bg=BG)
        info.pack(side="left", padx=(10, 0))
        tk.Label(info, text="Archivist", bg=BG, fg=TEXT,
                 font=F_TITLE).pack(anchor="w")
        tk.Label(info, text="Automatic file organizer", bg=BG, fg=MUTED,
                 font=F_SM).pack(anchor="w")

        # status pill (right)
        pill = tk.Frame(bar, bg=SURFACE, padx=10, pady=6)
        pill.pack(side="right", anchor="center")
        self._dot = tk.Label(pill, text="●", bg=SURFACE, fg=HINT,
                             font=("Segoe UI", 10))
        self._dot.pack(side="left", padx=(0, 5))
        self._status_lbl = tk.Label(pill, text="Idle", bg=SURFACE,
                                    fg=MUTED, font=F_SM)
        self._status_lbl.pack(side="left")

    # ── stats ────────────────────────────

    def _build_stats(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=20, pady=(0, 10))
        for col in range(3):
            row.columnconfigure(col, weight=1)

        self._sc_files  = StatCard(row, "Files moved")
        self._sc_files.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._sc_uptime = StatCard(row, "Uptime")
        self._sc_uptime.grid(row=0, column=1, sticky="nsew", padx=(0, 6))
        self._sc_events = StatCard(row, "Events")
        self._sc_events.grid(row=0, column=2, sticky="nsew")

    # ── paths ────────────────────────────

    def _build_paths(self):
        card = tk.Frame(self.root, bg=SURFACE, padx=16, pady=12)
        card.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(card, text="PATHS", bg=SURFACE, fg=HINT,
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(0, 6))

        self._dl_row  = PathRow(card, "Downloads folder", "↓", self._pick_downloads)
        self._dl_row.pack(fill="x")
        Divider(card)
        self._org_row = PathRow(card, "Organized folder", "⊞", self._pick_organized)
        self._org_row.pack(fill="x")
        Divider(card)
        self._db_row  = PathRow(card, "Database file",    "⬡", self._pick_db)
        self._db_row.pack(fill="x")

        # Populate path pickers with SettingsManager defaults (or explicit DB/default)
        dl_default = SettingsManager.get("downloads_dir", SettingsManager.DEFAULTS.get("downloads_dir"))
        org_default = SettingsManager.get("organized_dir", SettingsManager.DEFAULTS.get("organized_dir"))
        db_default = SettingsManager.get("database_url", SettingsManager.DEFAULTS.get("database_url"))

        if dl_default:
            self._dl_row.set(dl_default)
        if org_default:
            self._org_row.set(org_default)
        # show DB path with a note that it's the default when appropriate
        if db_default:
            self._db_row.set(f"{db_default}  (default)")

    # ── actions ──────────────────────────

    def _build_actions(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=20, pady=(0, 10))

        self._start_btn = IconButton(
            row, "▶   Start watcher",
            bg=ACCENT_BG, fg=ACCENT,
            active_bg=ACCENT, active_fg="black",
            command=self._start_watcher,
        )
        self._start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        IconButton(
            row, "■   Stop",
            bg=DANGER_BG, fg=DANGER,
            active_bg=DANGER, active_fg="black",
            command=self._stop_watcher,
        ).pack(side="left")

    # ── log ──────────────────────────────

    def _build_log(self):
        outer = tk.Frame(self.root, bg=SURFACE, padx=16, pady=12)
        outer.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # header row
        hdr = tk.Frame(outer, bg=SURFACE)
        hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="ACTIVITY LOG", bg=SURFACE, fg=HINT,
                 font=("Segoe UI", 7, "bold")).pack(side="left")
        tk.Button(hdr, text="Clear", bg=SURFACE, fg=HINT,
                  relief="flat", bd=0, font=F_SM, cursor="hand2",
                  activebackground=BORDER, activeforeground=TEXT,
                  command=self._clear_log).pack(side="right")

        # text + scrollbar
        inner = tk.Frame(outer, bg=SURFACE2)
        inner.pack(fill="both", expand=True)

        self._log = tk.Text(
            inner, bg=SURFACE2, fg=MUTED,
            font=F_MONO, relief="flat", bd=0,
            state="disabled", cursor="arrow",
            wrap="word", selectbackground=BORDER,
            insertbackground=TEXT,
        )
        self._log.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        sb = tk.Scrollbar(inner, command=self._log.yview,
                          bg=SURFACE2, troughcolor=SURFACE2,
                          activebackground=BORDER, relief="flat", bd=0)
        sb.pack(side="right", fill="y")
        self._log.configure(yscrollcommand=sb.set)

        # colour tags
        self._log.tag_configure("ts",      foreground=HINT)
        self._log.tag_configure("default", foreground=MUTED)
        self._log.tag_configure("info",    foreground=INFO)
        self._log.tag_configure("success", foreground=SUCCESS)
        self._log.tag_configure("warn",    foreground=WARNING)
        self._log.tag_configure("error",   foreground=DANGER)

        self._append("Archivist ready — configure paths and start the watcher.",
                     "default")

    # ──────────────────────────────────────
    #  PATH PICKERS
    # ──────────────────────────────────────

    def _pick_downloads(self):
        p = filedialog.askdirectory(title="Select Downloads Folder")
        if p:
            self._dl_row.set(p)
            self.log(f"Downloads folder: {p}", "info")

    def _pick_organized(self):
        p = filedialog.askdirectory(title="Select Organized Folder")
        if p:
            self._org_row.set(p)
            self.log(f"Organized folder: {p}", "info")

    def _pick_db(self):
        p = filedialog.asksaveasfilename(
            title="Database file",
            defaultextension=".db",
            filetypes=[("SQLite", "*.db"), ("All files", "*.*")],
        )
        if p:
            self._db_row.set(p)
            self.log(f"Database: {p}", "info")

    # ──────────────────────────────────────
    #  WATCHER
    # ──────────────────────────────────────

    def _start_watcher(self):
        dl = self._dl_row.get()
        if not dl:
            messagebox.showerror("Missing path",
                                 "Please select a Downloads folder first.")
            return
        if self._running:
            return

        db = self._db_row.get().replace("  (default)", "") or "data/archivist.db"
        os.makedirs(os.path.dirname(db) if os.path.dirname(db) else ".", exist_ok=True)

        Database.init(db)
        Database.connect()
        Database.create_tables([FileRecord, Settings])
        SettingsManager.init_defaults()

        self.watcher = FileWatcher(
            dl,
            ui_logger=self.log,
            on_file_moved=self._on_file_moved,
        )
        self.watcher_thread = threading.Thread(
            target=self.watcher.watch_start, daemon=True
        )
        self.watcher_thread.start()

        self._running     = True
        self._start_time  = time.time()
        self._files_moved = 0
        self._event_count = 0
        self._sc_files.set("0")
        self._sc_events.set("0")
        self._sc_uptime.set("0:00")

        self._set_status(True)
        self._start_btn.configure(text="▶   Running…", state="disabled",
                                  bg=BORDER, fg=HINT,
                                  activebackground=BORDER, activeforeground=HINT)
        self._tick()

        self.log("Database initialised.", "success")
        self.log(f"Watcher active — monitoring {dl}", "success")

    def _stop_watcher(self):
        if not self._running:
            self.log("Watcher is not running.", "warn")
            return
        self._running = False
        if self._uptime_job:
            self.root.after_cancel(self._uptime_job)
            self._uptime_job = None
        self._set_status(False)
        self._start_btn.configure(text="▶   Start watcher", state="normal",
                                  bg=ACCENT_BG, fg=ACCENT,
                                  activebackground=ACCENT, activeforeground="black")
        self.log("Watcher stopped.", "warn")

    def _tick(self):
        if not self._running:
            return
        e = int(time.time() - self._start_time)
        m, s = divmod(e, 60)
        self._sc_uptime.set(f"{m}:{s:02d}")
        self._uptime_job = self.root.after(1000, self._tick)

    # ──────────────────────────────────────
    #  PUBLIC CALLBACKS (thread-safe)
    # ──────────────────────────────────────

    def log(self, msg: str, level: str = "default"):
        """Log a line from any thread."""
        self.root.after(0, lambda: self._append(msg, level))

    def _on_file_moved(self):
        """Call from FileWatcher when a file is successfully organised."""
        self._files_moved += 1
        self._event_count += 1
        f, e = self._files_moved, self._event_count
        self.root.after(0, lambda: self._sc_files.set(f))
        self.root.after(0, lambda: self._sc_events.set(e))

    def increment_event(self):
        """Call from FileWatcher for non-move events (deletes, renames …)."""
        self._event_count += 1
        e = self._event_count
        self.root.after(0, lambda: self._sc_events.set(e))

    # ──────────────────────────────────────
    #  INTERNAL LOG
    # ──────────────────────────────────────

    def _append(self, msg: str, level: str = "default"):
        self._log.configure(state="normal")
        self._log.insert("end", _ts() + "  ", "ts")
        self._log.insert("end", msg + "\n", level)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _clear_log(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

    # ──────────────────────────────────────
    #  STATUS DOT
    # ──────────────────────────────────────

    def _set_status(self, active: bool):
        if active:
            self._dot.configure(fg=SUCCESS)
            self._status_lbl.configure(fg=SUCCESS, text="Watching")
        else:
            self._dot.configure(fg=HINT)
            self._status_lbl.configure(fg=MUTED, text="Idle")


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────

def run_ui():
    root = tk.Tk()
    ArchivistUI(root)
    root.mainloop()