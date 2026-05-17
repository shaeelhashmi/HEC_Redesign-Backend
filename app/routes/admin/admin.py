from flask import Blueprint, render_template, request, redirect, url_for
import secrets
import string

# 1. Define the blueprint (similar to const router = express.Router())
auth_blueprint = Blueprint('auth', __name__)

# 2. Define your routes on the blueprint
import secrets
from flask import Blueprint, render_template, request, redirect, session, current_app
from flask_mail import Message

auth_blueprint = Blueprint('auth', __name__)

# Hardcoded Admin Credentials
ADMIN_EMAIL = "shaeelh001@gmail.com"
ADMIN_PASSWORD = "SuperSecretAdminPassword123"  # Change this to your actual password

def generate_otp():
    # Generates a secure, random 6-digit number string
    return str(secrets.randbelow(900000) + 100000)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def admin_login():
    return render_template('admin_login.html')
@auth_blueprint.route('/callback', methods=['GET', 'POST'])
def login():
    return render_template('admin_login.html')