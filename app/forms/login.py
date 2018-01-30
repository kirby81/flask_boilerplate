from flask_wtf import FlaskForm
# Fields type
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
# Validators
from wtforms.validators import Email
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
