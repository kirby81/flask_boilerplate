from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature
from flask import current_app
from flask_login import UserMixin
from . import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User (UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        """Prevent clear access to the password"""
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Generate a new hash for the password and store it"""
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def verify_password(self, password):
        """Verify the password given in parameter with the password_hash"""
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """Generate a confirmation mail token"""
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def generate_reset_token(self, expiration=3600):
        """Generate a reset password token"""
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def confirm(self, token):
        """Confirm a user mail token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except BadSignature:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @staticmethod
    def reset_password(token, password):
        """Reset user's password"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except BadSignature:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = password
        db.session.add(user)
        return True


@login_manager.user_loader
def load_user(user_id):
    """Function to retrieve the logged-in user for Flask-Login"""
    return User.query.get(int(user_id))
