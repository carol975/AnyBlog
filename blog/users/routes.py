import secrets
import os

from blog import db, bcrypt, mail
from blog.users.forms import (RegistrationForm, LoginForm,
                        UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from blog.models import User, Post
from blog.users.utils import save_picture, send_reset_email

from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import login_user, logout_user, current_user, login_required

from sqlalchemy.exc import SQLAlchemyError


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
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
        except SQLAlchemyError as e:
            # TODO log errors
            flash(f'Sign Up Failed! Please try again', 'danger')

        flash(f'Your account has been created! You are now able to log in', 'success')
        # url_for the name of the function associated with the desired route
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')
            # TODO add check for next_page
            # https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work
            return redirect(next_page) if next_page else redirect(url_for('main.home'))

        else:
            flash('Login Failed', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    # flask login knows which user is logged in
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
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
        flash('Your account has been updated!', 'success')
        # do not return a rendered form, it will give a form resubmit error
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    # sessions :https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=str(username)).first_or_404()
    posts = Post.query.filter_by(author=user).\
        order_by(Post.date_posted.desc()).\
        paginate(per_page=5, page=page)
    return render_template('user_profile.html', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)
    if not user:
        flash('Link has expired', 'warning')
        return redirect(url_for('users.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            # TODO log errors
            flash(f'Password Reset Failed! Please try again', 'danger')
            return redirect(url_for('users.reset_request'))

        flash(f'Your password has been updated! You are now able to log in', 'success')
        # url_for the name of the function associated with the desired route
        return redirect(url_for('users.login'))

    return render_template('reset_password.html', title='Reset Password', form=form)
