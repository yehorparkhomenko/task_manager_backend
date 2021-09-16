from enum import EnumMeta
from typing import Text
from peewee import *

from model.base_model import BaseModel
from model.user import User


class Task(BaseModel):
    username = CharField()
    email = CharField()
    text = TextField()
    status = IntegerField()
    
