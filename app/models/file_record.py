from peewee import Model, CharField, TextField
from app.database.db import db

"""
fileRecord model represents a record of a file in the system, storing essential metadata such as the file path, filename, creation date, category, summary, and a hash for integrity verification. This model is used to track and manage files within the application, allowing for efficient organization and retrieval based on various attributes.
"""
class FileRecord(Model):
    path = CharField()
    filename = CharField()
    created_at = CharField()

    category = CharField(null=True)
    summary = TextField(null=True)

    file_hash = CharField(null=True)

    class Meta:
        database = db