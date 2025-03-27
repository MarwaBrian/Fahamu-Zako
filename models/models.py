from flask_sqlalchemy import SQLAlchemy
from . import db 
from werkzeug.security import generate_password_hash, check_password_hash




# Users Table
class User(db.Model):
    __tablename__ = 'users'
    user_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    second_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Store hashed password

    # Hash password before saving
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password validity
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)