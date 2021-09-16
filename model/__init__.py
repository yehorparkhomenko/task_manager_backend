import os

from .base_model import db
from .task import Task
from .user import User
from .token import Token

if not db.table_exists('task'):
    db.create_tables([Task])

if not db.table_exists('User'):
    db.create_tables([User])

if not db.table_exists('Token'):
    db.create_tables([Token])





