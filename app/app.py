from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db

# Init app
app = Flask(__name__)
app.config.from_object('config.DevConfig')
# Init database
db.init_app(app)
