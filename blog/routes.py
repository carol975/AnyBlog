from blog import app, db, bcrypt
from blog.forms import RegistrationForm, LoginForm
from blog.models import User, Post

from flask import render_template, url_for, flash, redirect
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
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You are logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Failed', 'danger')

    return render_template('login.html', title='Login', form=form)
    