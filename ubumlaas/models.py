from ubumlaas import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, username, password):
        """User constructor
        
        Arguments:
            email {string} -- User's email
            username {string} -- User name identifer
            password {string} -- User's password
        """
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Compare input password with current password
        
        Arguments:
            password {string} -- Input password
        
        Returns:
            boolean -- True if both password match, instead False 
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Email: {self.email} Username: {self.username}"

    def __str__(self):
        return self.__repr__() + f" Email: {self.email}"