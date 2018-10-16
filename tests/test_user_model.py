import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
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