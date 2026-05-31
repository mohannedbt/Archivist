from peewee import SqliteDatabase
import os


db = SqliteDatabase(None)


class Database:
    @classmethod
    def init(cls, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.init(db_path)

    @classmethod
    def connect(cls):
        db.connect()

    @classmethod
    def create_tables(cls, models):
        db.create_tables(models)