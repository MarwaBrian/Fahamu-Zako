from flask import Blueprint, render_template, request, redirect, url_for, session,flash

# from models.user import User
# from app import db

approutes_bp = Blueprint("approutes", __name__)

@approutes_bp.route('/')
def index():
    return render_template('index.html')

@approutes_bp.route('/legalSupport')
def legalSupport():
    if 'user_ID' in session:
        # User is logged in, show personalized experience
        return render_template('legalsupport.html', user_logged_in=True)
    else:
        # Guest user, show limited features and a login prompt
        flash('Login for a personalized experience.', 'info')
        return render_template('legalsupport.html', user_logged_in=False)
    
    

