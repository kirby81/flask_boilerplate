from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def add_permission(self, perm):
        """Add a permission to the role"""
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """Remove a permission to the role"""
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """Remove all permissions to the role"""
        self.permissions = 0

    def has_permission(self, perm):
        """Check if the role got the permission"""
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        """Roles fixture"""
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                              Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class User (UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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

    def generate_email_token(self, new_email, expiration=3600):
        """Generate a change email token"""
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email}).decode('utf-8')

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

    def change_email(self, token):
        """Change the user email with an email token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except BadSignature:
            return False
        if data.get('change_email') != self.id:
            return False
        if data.get('new_email') is None or self.query.filter_by(email=data.get('new_email')).first() is not None:
            return False
        self.email = data.get('new_email')
        db.session.add(self)
        return True

    def can(self, perm):
        """Check if the user got the permission"""
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        """Check if the user is an administrator"""
        return self.can(Permission.ADMIN)

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


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """Function to retrieve the logged-in user for Flask-Login"""
    return User.query.get(int(user_id))
