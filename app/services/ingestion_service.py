from app.helper.FileHelper import get_file_info, move_file
from app.models.file_record import FileRecord
from app.config.setting_manager import SettingsManager


class IngestionService:

    @staticmethod
    def process(filepath: str):
        """
        Main pipeline entry:
        file → extract → classify → store → move
        """

        # 1. ignore duplicates
        if FileRecord.get_or_none(FileRecord.path == filepath):
            return

        # 2. extract + classify + summarize
        info = get_file_info(filepath)

        # 3. store in DB
        record = FileRecord.create(
            path=info["path"],
            filename=info["filename"],
            created_at=info["created_at"],
            category=info["category"],
            summary=info["summary"],
            file_hash=info["file_hash"]
        )

        # 4. move file to organized folder
        base_dir = SettingsManager.get("organized_dir") or "data/organized"
        target_dir = f"{base_dir}/{info['category']}"

        move_file(filepath, target_dir)

        print(f"[INGESTED] {info['filename']} → {info['category']}")
        return record