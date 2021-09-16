import datetime

from flask import request
from flask_cors import cross_origin
from playhouse.shortcuts import model_to_dict

from main import app
from model import Task, User, Token
from utils import *


@app.route('/')
@cross_origin()
def index():
    developer_name = request.args.get('developer')
    if developer_name == None:
        return {
            "status": "error",
            "message": "Не передано имя разработчика"
        }

    sort_field = request.args.get('sort_field')
    sort_direction = request.args.get('sort_direction')
    page = request.args.get('page')
    paginate_by = 3

    if sort_field == None:
        sort_field = 'id'
    
    if sort_direction == None:
        sort_direction = 'asc'
    
    if page == None:
        page = 1

    response = validate_sorting_params(sort_field, sort_direction, page)

    page = int(page)

    if response["status"] == "error":
        return response
    
    if sort_field == 'id':
        order_by = Task.id
    elif sort_field == 'username':
        order_by = Task.username
    elif sort_field == 'email':
        order_by = Task.email
    elif sort_field == 'status':
        order_by = Task.status

    if sort_direction == 'asc':
        order_by = order_by.asc()
    elif sort_direction == 'desc':
        order_by = order_by.desc()

    tasks = Task.select().order_by(order_by).paginate(page, paginate_by)
    dict_tasks = [model_to_dict(task) for task in tasks]

    all_tasks = Task.select()
    
    return {
        "status": "ok",
        "message": {
            "tasks": dict_tasks
        },
        "total_task_count": len(all_tasks)
    }


@app.route('/create', methods=['POST']) 
@cross_origin()
def create():
    developer_name = request.args.get('developer')
    if developer_name == None:
        return {
            "status": "error",
            "message": "Не передано имя разработчика"
        }

    token = request.form.get('token')
    username = request.form.get('username')
    email = request.form.get('email')
    text = request.form.get('text')
    status = 0

    response = check_token(token)

    if response["status"] == "error":
        return response

    response = validate_task(username, email, text)

    if response["status"] == "error":
        return response

    response = check_username(username)

    if response["status"] == "error":
        return response

    task = Task(email=email, text=text, username=username, status=status)
    task.save()

    return {
        "status": "ok",
        "message": {
            "id": task.get_id(),
            "username": username,
            "email": email,
            "text": text,
            "status": status
        }
    }


@app.route('/edit/<int:task_id>', methods=['POST']) 
@cross_origin()
def edit(task_id):
    developer_name = request.args.get('developer')
    if developer_name == None:
        return {
            "status": "error",
            "message": "Не передано имя разработчика"
        }

    token_str = request.form.get('token')
    text = request.form.get('text')
    status = request.form.get('status')

    response = check_token(token_str)

    if response["status"] == "error":
        return response

    response = validate_status(status)

    if response["status"] == "error":
        return response

    if status != None:
        status = int(status)

    try: 
        task = Task.get_by_id(task_id)
    except:
        return {
            "status": "error",
            "message": {
                "id": "Такой задачи не существует"
            }
        }

    if status != None and is_admin(token_str) and task.text != text:
        if status == 0:
           task.status = 1
        elif status == 10:
            task.status = 11
    elif status == None and is_admin(token_str) and task.text != text:
        if task.status == 0:
            task.status = 1
        elif status == 10:
            task.status = 11
    elif status != None:
        task.status = status
        
    if text != None:
        task.text = text

    task.save()

    return {
        "status": "ok",
    }


@app.route('/login', methods=['POST']) 
@cross_origin()
def login():
    developer_name = request.args.get('developer')
    if developer_name == None:
        return {
            "status": "error",
            "message": "Не передано имя разработчика"
        }

    username = request.form.get('username')
    password = request.form.get('password')
    response = validate_credentials(username, password)

    if response["status"] == "error":
        return response

    try: 
        user = User.get(User.username == username, User.password_hash == gen_hash(password))
    except:
        return {
            "status": "error",
            "message": {
                "password": "Неверный логин или пароль"
            }
        }
    
    token_str = gen_token()
    token = Token(user=user, token=token_str, expires=datetime.datetime.now() + datetime.timedelta(days=1))
    token.save()

    return {
        "status": "ok",
        "message": {
            "token": token_str
        }
    }
    
    
@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    developer_name = request.args.get('developer')
    if developer_name == None:
        return {
            "status": "error",
            "message": "Не передано имя разработчика"
        }

    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin')

    response = validate_credentials(username, password, is_admin)    

    if response["status"] == "error":
        return response

    if is_admin == 'true':
        is_admin = True
    elif is_admin == 'false' or is_admin == None:
        is_admin = False
    

    users = User.select().where(User.username == username)
    
    if len(users) > 0:
        return {
            "status": "error",
            "message": {
                "username": "Такой логин уже существует"
            }
        }
    
    user = User(username=username, password_hash=gen_hash(password), is_admin=is_admin)
    user.save()
    
    token_str = gen_token()
    token = Token(user=user, token=token_str, expires=datetime.datetime.now() + datetime.timedelta(days=1))
    token.save()

    return {
        "status": "ok",
        'message': {
            "token": token_str
        }
    }
