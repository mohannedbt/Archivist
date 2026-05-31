from peewee import Model, CharField, TextField
from app.database.db import db

"""
Settings model represents a key-value pair for application configuration stored in the database. Each setting has a unique key and a corresponding value, allowing for flexible and dynamic configuration management. This model is used by the SettingsManager to initialize default settings and manage application configurations without hardcoding values in the codebase.

"""

class Settings(Model):
    key = CharField(unique=True)
    value = TextField()

    class Meta:
        database =db