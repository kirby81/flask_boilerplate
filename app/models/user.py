from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from models import db

from models.queries.user_query import UserQuery


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    query_class = UserQuery

    def __init__(self, email, password, username=None):
        self.email = email
        self.set_password(password)
        self.username = username

    def __repr__(self):
        return '<User {}> {}'.format(self.id, self.username)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)