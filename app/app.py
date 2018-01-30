from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user

from models import db
from models.user import User

from forms.signup import SignupForm
from forms.login import LoginForm

# Init app
app = Flask(__name__)
app.config.from_object('config.DevConfig')
# Init database
db.init_app(app)
# Init login
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return 'Hello World !'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(
                    form.email.data,
                    form.password.data,
                    form.username.data
                )
                db.session.add(new_user)
                db.session.commit()
                return 'User success'
            except IntegrityError:
                return 'Email already exist'
    else:
        return 'Problem on signup'

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.authenticate(
                form.email.data,
                form.password.data
            )
            if user is not None:
                login_user(user)
                return redirect(url_for('home'))
        error = 'Invalid username or password. Please try again!'
    return render_template('login.html', form=form, error=error)

@app.route('/home')
@login_required
def home():
    return 'Home page'