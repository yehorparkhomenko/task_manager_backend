from peewee import * 

db_path = 'database.db'
db = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = db

