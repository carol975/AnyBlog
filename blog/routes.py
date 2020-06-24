import secrets
import os

from blog import app, db, bcrypt
from blog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from blog.models import User, Post

from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError


posts = [
    {
        'author': 'carol',
        'title': 'blg 1',
        'content': 'first blg',
        'date_posted': 'April 20, 2020'
    },
    {
        'author': 'carol',
        'title': 'blg 2',
        'content': 'first blg',
        'date_posted': 'April 20, 2020'
    },
]



@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    # don't have to pass request.form to Flask-WTF; it will load automatically. 
    # validate_on_submit will check if it is a POST request and if it is valid.
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        
        try:
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in', 'success')
        except SQLAlchemyError as e:
            #TODO log errors
            flash(f'Sign Up Failed! Please try again', 'danger')
        
        # url_for the name of the function associated with the desired route
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            next_page = request.args.get('next')
            #TODO add check for next_page
            # https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work
            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash('Login Failed', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    # flask login knows which user is logged in
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', 'profile_pics', picture_fn)
    
    #resize image to 125x125 pixel
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
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
        db.session.commit()
        flash('Your account has been updated!', 'success')
        # do not return a rendered form, it will give a form resubmit error
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    # sessions :https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account', image_file=image_file, form=form)

# TODO use blueprint to separate the routes
@app.route('/post/new')
@login_required
def new_post():
    # flask login knows which user is logged in
    logout_user()
    return render_template('create_post.html', title='New Post')
