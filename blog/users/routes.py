mport secrets
import os

from blog import db, bcrypt, mail
from blog.users.forms import (RegistrationForm, LoginForm,
                        UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from blog.models import User, Post
from blog.users.utils import save_picture, send_reset_email

from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint,
                   Response, jsonify)
from flask_login import login_user, logout_user, current_user, login_required

from sqlalchemy.exc import SQLAlchemyError


users = Blueprint('users', __name__)


@users.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return Response(status=200)

    form = RegistrationForm(csrf_enabled=False)
    # don't have to pass request.form to Flask-WTF; it will load automatically.
    # validate_on_submit will check if it is a POST request and if it is valid.
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)

        try:
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in', 'success')
        except SQLAlchemyError as e:
            print(e)
            # TODO log errors
            # url_for the name of the function associated with the desired route
            return Response(status=500)
        return Response(status=200)
    return Response(status=400)


@users.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        print("is logged in")
        return Response(status=200)

    form = LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return Response(status=200)
        return Response(status=401)
    return Response(status=400)

@users.route('/logout')
def logout():
    # flask login knows which user is logged in
    logout_user()
    return Response(status=200)


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():     
    if request.method == 'POST':
        form = UpdateAccountForm(csrf_enabled=False)
        if form.validate_on_submit():
            if form.picture.data:
                # TODO use external picture server
                # TODO remove previous user picture if exist
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file

            current_user.username = form.username.data
            current_user.email = form.email.data
            # if user already in database then dont need to do db.session.add()
            db.session.commit()
        
            return Response(status=200)

    elif request.method == 'GET':
        # sessions :https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
        profile_image_url = url_for('static', filename='profile_pics/' + current_user.image_file, _external=True)
        data = {
            'username': current_user.username,
            'email' : current_user.email,
            'profile_image_url': profile_image_url
        }
        return Response(status=200)
    
    return Response(status=400)
  
    


@users.route("/user/<string:username>")
def user_profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=str(username)).first or None
    if not user:
        return Response(status=400)
    
    posts = Post.query.filter_by(author=user).\
        order_by(Post.date_posted.desc()).\
        paginate(per_page=5, page=page)
    
    items = [post.serialize_summary() for post in posts.items]
    data = {
        'items': items,
        'curr_page': posts.page,
        'total_page': posts.pages

    }
    return Response(json.dumps(data), status=200)



@users.route('/reset_password', methods=['POST'])
def reset_request():
    if current_user.is_authenticated:
        return Response(status=403)

    if form.validate_on_submit():
        form = RequestResetForm(csrf_enabled=False)
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        return Response(status=200)

    return Response(status=400)
    


@users.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_token(token):
    if request.method == 'GET':
        if current_user.is_authenticated:
            return Response(status=403)

        user = User.verify_reset_token(token)
        if not user:
            return Response(status=410)
    else:
        form = ResetPasswordForm(csrf_enabled=False)
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            user.password = hashed_password

            try:
                db.session.commit()
            except SQLAlchemyError as e:
                # TODO log errors
                return Response(status=500)

            flash(f'Your password has been updated! You are now able to log in', 'success')
            # url_for the name of the function associated with the desired route
            return Response(status=200)

        return Response(status=400)
