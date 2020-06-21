from blog import app, db, bcrypt
from blog.forms import RegistrationForm, LoginForm
from blog.models import User, Post

from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user, login_required
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

@app.route("/account")
@login_required
def account():
    return render_template('account.html',title='Account')