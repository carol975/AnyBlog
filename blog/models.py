from datetime import datetime
from dataclasses import dataclass
from flask import current_app, json, url_for
from flask_login import UserMixin 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer 
from blog import db, login_manager

'''
user loader decorator evaluates the following:
1 is user authenticated
2 is actor
3 is anonymous
4 get id
'''
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@dataclass
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    
    # A one to many relationship places a foreign key on the child table referencing the parent. 
    # relationship() is then specified on the parent, 
    # as referencing a collection of items represented by the child
    # https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
    # relationships: https://docs.oracle.com/cd/E19798-01/821-1841/bnbqi/index.html

    #runs a query to get posts with user_id = this user id
    # each post has a ref to the user. 
    # post.author = this user object
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id) 

    def __repr__(self):
        return json.dumps({'username': self.username, 'email':self.email, 'profile_image': self.image_file})
    
    def to_json(self):
        return {'username': self.username, 'email':self.email, 
            'profile_image': url_for('users.get_image', image_name=self.image_file)}

@dataclass
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # pass datetime function instead of an instance of the datetime function.
    # because the instance would return the time at which the model is created
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return json.dumps({'title': self.title, 'content':self.content, 'date_posted': self.date_posted,'author_username': self.author.username, 'author_user_id': self.author.id})

    def to_json(self):
        return {'post_id':self.id, 'title': self.title, 'content':self.content, 'date_posted': self.date_posted, 'author_username': self.author.username, 'author_user_id': self.author.id, 'author_profile_picture':  url_for('static', filename='profile_pics/' + self.author.image_file)}
    
    def to_json_summary(self):
        return {'post_id':self.id, 'title': self.title, 'summary':self.summary, 'author_user_id':self.author.id}