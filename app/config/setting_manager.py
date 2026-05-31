from app.models.settings import Settings

"""

SettingsManager is responsible for managing application settings stored in the database. It provides methods to initialize default settings, retrieve specific settings, and update settings as needed. This allows for a centralized way to manage configuration values that can be easily modified without changing the codebase.

"""
class SettingsManager:

    DEFAULTS = {
        "downloads_dir": "C:/Users/user/Downloads",
        "organized_dir": "data/organized",
        "database_url": "data/archivist.db",
        "allowed_extensions": ".pdf,.txt,.jpg,.png",
        "log_level": "INFO"
    }

    @classmethod
    def init_defaults(cls):
        for key, value in cls.DEFAULTS.items():
            if not Settings.select().where(Settings.key == key).exists():
                Settings.create(key=key, value=value)

    @classmethod
    def get(cls, key: str):
        setting = Settings.get_or_none(Settings.key == key)
        return setting.value if setting else None

    @classmethod
    def set(cls, key: str, value: str):
        setting = Settings.get_or_none(Settings.key == key)

        if setting:
            setting.value = value
            setting.save()
        else:
            Settings.create(key=key, value=value)