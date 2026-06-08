from app.database.db import Database
from app.models.file_record import FileRecord
from app.config.setting_manager import SettingsManager
from app.models.settings import Settings
from app.extractors import router as rt
from app.watcher.file_watcher import FileWatcher as fw
import os
path="/home/mohanned/Downloads"
import threading
print(os.path.isdir(path))
import threading
import time

def viewing():
    seen = set()

    while True:
        with open("file.txt", "a", encoding="utf-8") as f:
            for record in FileRecord.select():
                if record.filename in seen:
                    continue

                print(record.filename, record.category)
                f.write(record.filename + "\n")
                seen.add(record.filename)

        time.sleep(2)  
if __name__ == "__main__":

    DATABASE_URL = SettingsManager.DEFAULTS["database_url"]
    Database.init(DATABASE_URL)
    Database.connect()
    Database.create_tables([FileRecord,Settings])
    file=fw(path)
    #t1=threading.Thread(target=file.WatchStart)
    #t1.start()
    print(rt.extract("/home/mohanned/Downloads/Présentation-de-lentreprise-Corrigé.docx"))
    print(rt.extract("/home/mohanned/Downloads/Untitled-2026-02-20-1123.png"))


