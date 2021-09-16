import os
import hashlib
from base64 import b64encode
import secrets
import hashlib
import re
import json
import datetime

from flask import request
from flask_cors import CORS, cross_origin
from peewee import DateTimeField
from playhouse.shortcuts import model_to_dict

from main import app
from model import Task, User, Token


def gen_hash(password):
    return hashlib.sha512(password.encode('UTF-8')).hexdigest()


def gen_token():
    return secrets.token_hex(16)

def validate_sorting_params(sort_field: str, sort_direction: str, page) -> dict():
    response = {
        "status": "ok",
        "message": dict()
    }
    
    if sort_field not in ['id', 'username', 'email', 'status']:
        response["status"] = "error"
        response["message"]["sort_field"] = "sort_field указан неверно"

    if sort_direction not in ['asc', 'desc']:
        response["status"] = "error"
        response["message"]["sort_direction"] = "sort_direction указан неверно"

    try:
        page = int(page)
    except :   
        response['status'] = "error"
        response["message"]["page"] = "page указан неверно"

    if len(response["message"].keys()) == 0:
        del response["message"]

    return response



def validate_credentials(username: str, password: str, is_admin=None) -> dict():
    response = {
        "status": "ok",
        "message" : dict()
    }

    if username == None:
        response["status"] = "error"
        response["message"]["username"] = "Поле является обязательным для заполнения"

    if password == None:
        response["status"] = "error"
        response["message"]["password"] = "Поле является обязательным для заполнения"

    if is_admin not in ['true', 'false'] and is_admin != None:
        response["status"] = "error"
        response["message"]["is_admin"] = "Поле имеет неверный формат"
    
    if len(response["message"].keys()) == 0:
        del response["message"]

    return response


def validate_task(username: str, email: str, text: str) -> dict():
    response = {
        "status": "ok",
        "message": dict()
    }

    if username == None:
        response['status'] = "error"
        response['message']['username'] = "Поле является обязательным для заполнения"

    if email == None:
        response['status'] = "error"
        response['message']['email'] = "Поле является обязательным для заполнения"
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        response['status'] = "error"
        response['message']['email'] = "Неверный email"
 
    if text == None:
        response['status'] = "error"
        response['message']['text'] = "Поле является обязательным для заполнения"

    if len(response["message"].keys()) == 0:
        del response["message"]

    return response


def validate_status(status):
    response = {
        "status": "ok",
        "message": dict()
    }

    if status not in ['0', '10'] and status != None:
        response['status'] = 'error'
        response['message']['status'] = "Поле имеет неверный формат"
 
    if len(response["message"].keys()) == 0:
        del response["message"]
   
    return response


def check_token(token_str): 
    try: 
        token = Token.get(Token.token == token_str)
    except:
        return {
            "status": "error",
            "message": {
                "token": "Вы не авторизированы"
            }
        }

    if token.expires < datetime.datetime.now():
        return {
            "status": "error",
            "message": {
                "token": "Токен истек"
            }
        }

    return {
        "status": "ok"
    }


def check_username(username):
    try: 
        user = User.get(User.username == username)
    except:
        return {
            "status": "error",
            "message": {
                "username": "Такого пользователя не существует"
            }
        }
    
    return {
        "status": "ok"
    }


def is_admin(token_str): 
    token = Token.get(Token.token == token_str)
    return token.user.is_admin
