# from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, request
# from flask_login import current_user, login_required, logout_user, login_user
# from app import db, bcrypt
# from models import User
# from forms import RegistrationForm, LoginForm
# from flask_wtf import FlaskForm

# auth = Blueprint('auth', __name__)

# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('auth.home'))
#     form  = RegistrationForm()
#     if form.validate_on_submit():
#         try:
#             hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#             user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#             db.session.add(user)
#             db.session.commit()
#             flash('Your account has been created successfully! You are now able to log in.', 'success')
#             return redirect(url_for('auth.login'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'An error occurred. {str(e)} Please try again.', 'danger')
#     return render_template('register.html', title='Register', form=form)

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('auth.home'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user, remember=form.remember.data)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('auth.home'))
#         else:
#             flash('Login unsuccessful. Please check your email and password.', 'danger')
#     return render_template('./templates/login.html', title='Login', form=form)

# @auth.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('auth.dashboard'))

# @auth.route('/user')
# @login_required
# def dashboard():
#     return 'Welcome to the user page!'

# @auth.route('/')
# def home():
#     return render_template('base.html', title = 'main page')
