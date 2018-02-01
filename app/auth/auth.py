from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from flask_login import current_user

from auth.forms.signup import SignupForm
from auth.forms.login import LoginForm
from auth.services.auth_service import AuthService

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = AuthService.signup(form)
            if user is not None:
                return redirect(url_for('home'))
            return 'User already exist'
    if current_user.is_authenticated():
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None

    if request.method == 'POST':
        if form.validate_on_submit():
            user = AuthService.login(form)
            if user is not None:
                return redirect(url_for('home'))
        error = 'Invalid username or password. Please try again!'
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html', form=form, error=error)
