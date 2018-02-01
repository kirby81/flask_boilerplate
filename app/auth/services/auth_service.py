from models import db
from models.user import User

from sqlalchemy.exc import IntegrityError

from flask_login import login_user

from auth.forms.signup import SignupForm

class AuthService(object):

    @staticmethod
    def signup(signup_form):
        try:
            new_user = User(
                signup_form.email.data,
                signup_form.password.data,
                signup_form.username.data
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
        except IntegrityError:
            return None
        return new_user

    @staticmethod
    def login(login_form):
        user = User.query.authenticate(
            login_form.email.data,
            login_form.password.data
        )
        if user is not None:
            login_user(user)
        return user
