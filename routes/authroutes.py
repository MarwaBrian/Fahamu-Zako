import re  # Import regular expressions for password validation
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from models import db
from models.models import User


#Define Blueprints
Login_bp = Blueprint("login", __name__)
signup_bp = Blueprint("signup", __name__)


# Password validation function
def is_strong_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character."
    return None  # Password is strong

#Signup Functionality
@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        Uname = request.form.get('Uname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print(f"Received: {fname}, {lname},{lname}, {email}, {password}, {confirm_password}")  # Debugging output

        # Validate inputs
        if not (fname and lname and lname and email and password and confirm_password):
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup.signup'))
        
        # Check password strength
        password_error = is_strong_password(password)
        if password_error:
            flash(password_error, 'danger')
            return redirect(url_for('signup.signup'))
        
        #checks if username exists
        existing_user = User.query.filter_by(username=Uname).first()
        if existing_user:
            flash('Username already registered. Please login.', 'warning')
            return redirect(url_for('signup.signup'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('signup.signup'))
        


        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(first_name=fname, second_name=lname, username=Uname, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Log in user automatically
        session['user_ID'] = new_user.user_ID
        session['email'] = new_user.email

        flash('Signup successful! Welcome to Funza Mama.', 'success')
        return redirect(url_for('approutes.legalsupport'))  # Redirect to dashboard after signup

    return render_template('signup.html')

#Login Functionality 
@Login_bp.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Store session data
            session['user_ID'] = user.user_ID
            session['email'] = user.email

            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('approutes.legalSupport'))  # Redirect after login
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login.login'))  # Stay on login page if failed

    return render_template('login.html')


#Logout Functionlaity
@Login_bp.route('/logout')
def logout():
    session.pop('user_ID', None)  # Remove user session
    session.pop('email', None)  # Remove email from session (optional)
    
    flash('You have been logged out.', 'success')
    return redirect(url_for('approutes.index'))  # Redirect to login page after logout
