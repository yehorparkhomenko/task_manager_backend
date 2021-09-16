from peewee import *

from model.base_model import BaseModel


class User(BaseModel):
    username = CharField()
    password_hash = CharField()
    is_admin = BooleanField(default=False)
