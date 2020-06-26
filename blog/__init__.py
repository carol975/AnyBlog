import os 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '5a19965ca8ff8a93848a69c64b5a93ff' #use python secret module
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

'''
init db: from blog import db, User, Post
db.create_all()
user_1 = User(...)
db.session.add(user_1)
db.session.commit()

see users

User.query.all()

'''
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please Login'
login_manager.login_message_category = 'info' # bootstrap class

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PW')

mail = Mail(app)

from blog.users.routes import users
from blog.posts.routes import posts
from blog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)