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
        u = User(password='foo')
        u2 = User(password='bar')
        self.assertTrue(u.password_hash != u2.password_hash)
