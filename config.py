import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/fahamuhakizako_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
