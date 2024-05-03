from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, leave_room

from datetime import datetime

12
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'NzqEI!@mcV4KfP7DU'



socketio = SocketIO(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)



class Room_User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer)
    id_room = db.Column(db.Integer)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_room = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_room = db.Column(db.Integer)
    msg = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    id_sender = db.Column(db.Integer)

@app.route("/", methods=['GET', 'POST'])
def home():
    if session.get('user_tag_name'):
        if session.get('room'):
            return render_template('dialogue.html')
            #users = User.query.all()
            #return render_template("all_users.html", users=users)
        else:
            if request.method == "POST":
                id_room = int(request.form["room_number"])
                room = Room.query.filter_by(id_room=id_room).first()

                if room:
                    session["room"] = room
                    join_room(room)
                    return render_template("dialogue.html")
                flash('Такого чата не существует!')
            return render_template('hub.html')
            #return "Выберите чат, чтобы начать общаться!"
    return render_template("index.html")


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form['Username']
        password = request.form['Password']
        confirm_password = request.form['Confirm_password']
        tag_name = request.form['User_tag_name']

        if not (1 <= len(username) <= 15):
            flash('Недопустимая длина имени')
        elif not (1 <= len(tag_name) <= 15):
            flash('Недопустимая длина тега')
        elif tag_name[0] != '@':
            flash("Недопустимый тег")
        elif User.query.filter_by(tag_name=tag_name).first():
            flash("Такой тег уже занят!")
        elif password != confirm_password:
            flash('Пароли не совпадают')
        elif len(password) < 8:
            flash("Длина пароля меньше допустимой")

        else:
            new_user = User(name=username, password=password, tag_name=tag_name)

            print(f'New account with the name of {username} was successfully created!')



            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect('/')
            except:
                return 'error'

    return render_template('register.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":

        tag_name = request.form['User_tag_name']
        entered_password = request.form['Password']
        
        user = User.query.filter_by(tag_name=tag_name).first()

        if user:
            correct_password = user.password
            if correct_password == entered_password:
                session['user_tag_name'] = tag_name
                session['room'] = None
                flash('Вы успешно вошли в аккаунт')
                try:
                    return redirect('/')
                except:
                    return 'error'
                
        flash('Неправильные тег или пароль')
        
    return render_template('login.html')

@app.route("/<int:user_id>")
def info(user_id):
    user = User.query.get(user_id)
    return render_template('user_info.html', user=user)


@socketio.on('connect')
def connect():
    print(f'my G just connected to the {session["room"]} room')
    


@socketio.on('message')
def send_message(data):
    print('received message:', data)
    socketio.send(data['data'], to=1)
