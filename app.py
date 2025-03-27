from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db  # Import db from models/__init__.py
from models.models import User # Import models

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow 

app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)


# Import models to register them
with app.app_context():
    from models.models import *


from routes.authroutes import Login_bp, signup_bp
from AI_model.modelIntegration import chat_bp
from routes.approutes import approutes_bp


# Register Blueprints (modular routes)
app.register_blueprint(Login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(approutes_bp)
app.register_blueprint(chat_bp, url_prefix="/chat")  # Register the blueprint


print(app.url_map)



if __name__ == '__main__':
    app.run(debug=True)
