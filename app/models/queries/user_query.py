from flask_sqlalchemy import BaseQuery

class UserQuery(BaseQuery):

    def authenticate(self, email, password):
        user = self.filter_by(email=email).first()
        if user is not None:
            if user.check_password(password):
                return user
            user = None
        return user