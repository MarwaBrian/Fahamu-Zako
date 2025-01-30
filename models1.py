from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
# from app import app

db = SQLAlchemy()# Initialize the database


ROLE_USER = 'user'
# ROLE_PR_USER = 'pr_user'
# ROLE_ADMIN = 'admin'

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
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

""" 
2. Define the Database Schema (models.py)
Start with the database model because authentication systems rely heavily on storing user data.

What to include in the schema:
User Table:
Fields: id, username, email, password_hash.
Add constraints (e.g., unique username and email).
Password Hashing:
Ensure you plan to hash passwords before storing them.
3. Plan and Configure Authentication Logic
Once the database model is ready, think about the authentication flow.

Logic to Implement:
Signup Process:

Validate user inputs (e.g., unique username/email, strong password).
Hash the password.
Store user data in the database.
Login Process:

Validate user credentials by checking the stored password hash.
Set up a session mechanism to track logged-in users.
Session Management:

Use Flask's session object to store user-specific data like user_id.
Add session timeout and secure cookies.
Logout Process:

Clear session data to log the user out.
4. Set Up Form Handling (forms.py)
Next, work on handling input validation for forms. Use Flask-WTF to simplify this process.

Forms to Implement:
Signup Form:
Fields: username, email, password, confirm_password.
Validations: Required fields, unique email/username, strong password.
Login Form:
Fields: email, password.
Validations: Required fields, valid email.
5. Configure Routes (routes.py)
Define routes for signup, login, logout, and protected areas.

Key Routes:
/signup: Handles user registration.
/login: Handles authentication and session creation.
/logout: Clears session and redirects to the homepage.
/dashboard (or any protected page): Available only to authenticated users.
Implementation Tips:
Keep routes lean; delegate heavy logic to helper functions or utilities.
Implement error handling for scenarios like invalid login or duplicate signup.
6. Build Templates (templates/)
Now, create the user interface using HTML templates. Start with simple forms for signup and login.

Templates to Create:
signup.html: Displays the signup form.
login.html: Displays the login form.
dashboard.html: A sample protected page for logged-in users.
Use Jinja2 templating for dynamic content (e.g., error messages or user-specific data).

7. Add Security and Best Practices
Before running your app, ensure you incorporate security measures:

Password Hashing: Use werkzeug.security or bcrypt.
Session Security:
Set a secret key in config.py for signing cookies.
Secure cookies (SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY).
CSRF Protection: Use Flask-WTF or similar tools.
Input Validation: Ensure no malicious inputs reach your backend.
8. Test the Workflow
Test the signup and login functionality thoroughly:

Register a new user.
Log in with the registered credentials.
Access a protected route.
Log out and verify access is revoked.
Use unit testing libraries like pytest or unittest for automated testing.

9. Incremental Improvements
Once basic authentication is working:

Add features like password reset, email verification, or two-factor authentication.
Consider integrating token-based authentication (e.g., JWT) if you plan to expand to APIs.
Starting Point
Start with the database schema in models.py, followed by form handling in forms.py. Once those are ready, proceed to implement routes in routes.py and connect them to the templates.


"""