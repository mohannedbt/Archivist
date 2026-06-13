import os
from app.models.settings import Settings


class SettingsManager:

    DEFAULTS = {
        "downloads_dir": os.path.join(os.path.expanduser("~"), "Downloads"),
        "organized_dir": "data/organized",
        "database_url": "data/archivist.db",
        "allowed_extensions": ".pdf,.txt,.jpg,.png",
        "log_level": "INFO"
    }

    # -------------------------
    # INIT DEFAULTS
    # -------------------------
    @classmethod
    def init_defaults(cls):
        for key, value in cls.DEFAULTS.items():

            exists = Settings.select().where(Settings.key == key).exists()

            if not exists:
                Settings.create(key=key, value=str(value))

    # -------------------------
    # GET SAFE VALUE
    # -------------------------
    @classmethod
    def get(cls, key: str, default=None):
        setting = Settings.get_or_none(Settings.key == key)

        if not setting:
            return default

        return setting.value

    # -------------------------
    # REQUIRED GET (STRICT MODE)
    # -------------------------
    @classmethod
    def require(cls, key: str):
        setting = Settings.get_or_none(Settings.key == key)

        if not setting:
            raise KeyError(f"Missing required setting: {key}")

        return setting.value

    # -------------------------
    # SET / UPDATE
    # -------------------------
    @classmethod
    def set(cls, key: str, value):
        setting = Settings.get_or_none(Settings.key == key)

        if setting:
            setting.value = str(value)
            setting.save()
        else:
            Settings.create(key=key, value=str(value))