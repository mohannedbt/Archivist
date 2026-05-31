from app.database.db import Database
from app.models.file_record import FileRecord
from app.config.setting_manager import SettingsManager
from app.models.settings import Settings

if __name__ == "__main__":

    DATABASE_URL = SettingsManager.DEFAULTS["database_url"]
    Database.init(DATABASE_URL)
    Database.connect()
    Database.create_tables([FileRecord,Settings])

    FileRecord.create(
        path="data/raw/example.pdf",
        filename="example.pdf",
        created_at="2024-06-01 12:00:00",
        category="document",
        summary="An example PDF file",
        file_hash="abc123"
    )

    for record in FileRecord.select():
        print(record.filename, record.category)