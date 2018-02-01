from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flask_login import LoginManager
from flask_login import login_required

from models import db
from models.user import User

from auth import auth

# Init app
app = Flask(__name__)
app.register_blueprint(auth)
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

@app.route('/home')
@login_required
def home():
    return 'Home page'