from flask import Flask
from flask import request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import login_required

from models import db
from models.user import User

from services import loggin_manager
from forms.signup import SignupForm

# Init app
app = Flask(__name__)
app.config.from_object('config.DevConfig')
# Init database
db.init_app(app)
# Init login
loggin_manager.init_app(app)

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
                import pdb; pdb.set_trace()
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
    return 'Login page'

@app.route('/home')
@login_required
def home():
    return 'Home page'