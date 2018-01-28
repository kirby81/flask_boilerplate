from services import loggin_manager

# Model
from models.user import User


@loggin_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
