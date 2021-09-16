from enum import unique
from peewee import *

from model.base_model import BaseModel
from model.user import User


class Token(BaseModel):
    user = ForeignKeyField(User)
    token = CharField()
    expires = DateTimeField()

