import unittest
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        password = 'foo'
        u = User(password=password)
        self.assertTrue(u.password_hash is not None)
        self.assertTrue(u.password_hash != password)

    def test_no_password_getter(self):
        u = User(password='foo')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        password = 'foo'
        u = User(password=password)
        self.assertTrue(u.verify_password(password))
        self.assertFalse(u.verify_password('bar'))

    def test_password_salts_are_random(self):
        u1 = User(password='foo')
        u2 = User(password='bar')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='foo', id=1)
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='foo')
        token = u.generate_confirmation_token(expiration=-1)
        self.assertFalse(u.confirm(token))

    def test_confirmation_token_by_other_user(self):
        u1 = User(password='foo', id=1)
        u2 = User(password='bar', id=2)
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='foo')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'bar'))
        self.assertTrue(u.verify_password('bar'))

    def test_invalid_reset_token(self):
        u = User(password='foo')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'bar'))
        self.assertTrue(u.verify_password('foo'))

    def test_valid_change_email(self):
        u = User(email='foo@test.com', password='foo')
        token = u.generate_email_token('bar@test.com')
        self.assertTrue(u.change_email(token))
        self.assertEqual(u.email, 'bar@test.com')

    def test_invalid_change_email(self):
        u = User(email='foo@test.com', password='foo')
        token = u.generate_email_token('bar@test.com')
        self.assertFalse(u.change_email(token + 'a'))
        self.assertEqual(u.email, 'foo@test.com')

    def test_user_role(self):
        u = User(email='foo@test.com', password='bar')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_moderator_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='foo@test.com', password='bar', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='foo@test.com', password='bar', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
