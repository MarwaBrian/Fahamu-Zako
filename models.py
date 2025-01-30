from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()  # Initialize the db object here

ROLE_USER = 'user'
# ROLE_PR_USER = 'pr_user'
# ROLE_ADMIN = 'admin'

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_USER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.id)
    
    # def is_admin(self):
    #     return self.role == ROLE_ADMIN
    
    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        if len(password) < 8 or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password) or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            raise ValueError("Password must be at least 8 characters long, include at least one uppercase letter, one number, and one special character.")
        # Hash the password before storing it
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check if the provided password matches the stored hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.id}: {self.username}, {self.email}>"
