import os

import MySQLdb
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
import secrets

from flask import Flask

# 1. Define the blueprint (similar to const router = express.Router())


# 2. Define your routes on the blueprint
import secrets
from flask import Blueprint, render_template, request, redirect, session, current_app
from flask_mysqldb import MySQL
app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "shaeel_dev_secret_123")

# Add these lines to help cookies work on your local machine
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,  # Set to False because you are using http, not https
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=604800 # 1 hour
)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
mysql = MySQL(app)
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
@auth_blueprint.route('/dashboard')
def admin_dashboard():
    # If the session key doesn't exist, they can't see the dashboard

    if not session.get('is_admin_logged_in'):
        return render_template('admin_login.html')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM cnic")
    cnic_data = cursor.fetchall()
    unique_cnic = []
    for cnic in cnic_data:
        cnic_number = cnic.get('cnic_number')
        cnic_image = cnic.get('CNIC_Image')
        if not cnic_number and cnic_image:
            unique_cnic.append(cnic)
    print(unique_cnic)
    return render_template('hec-admin-dashboard.html', cnic_data=unique_cnic)
@auth_blueprint.route('/verify_user/<string:userId>', methods=['POST'])
def verify_user(userId):
    # 1. Security Check: Ensure only the admin can trigger this
    if not session.get('is_admin_logged_in'):
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    # 2. Extract the JSON data from the request body
    data = request.get_json()
    cnic_number = data.get('cnic_number')

    if not cnic_number or len(cnic_number) != 13:
        return jsonify({"success": False, "error": "Invalid CNIC format"}), 400

    # 3. Update the Database
    try:
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM cnic WHERE cnic_number = %s"
        cursor.execute(sql, (cnic_number,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"success": False, "error": "CNIC number already exists"}), 400

        sql = "UPDATE cnic SET cnic_number = %s WHERE email = %s"
        cursor.execute(sql, (cnic_number, userId))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"success": True, "message": "User verified successfully"}), 200
    
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify({"success": False, "error": "Database update failed"}), 500
@auth_blueprint.route('/logout')
def admin_logout():
    # Remove the specific admin key from the session
    session.pop('is_admin_logged_in', None)
    
    # Optional: Clear the entire session if you want a total reset
    # session.clear() 
    
    return render_template('admin_login.html')
@auth_blueprint.route('/check', methods=['POST'])
def admin_check():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # HARDCODED CREDENTIALS
    ADMIN_USER = "shaeel_admin"
    ADMIN_PASS = "HEC_Secure_2026!" # Use a strong password

    if username == ADMIN_USER and password == ADMIN_PASS:
        session['is_admin_logged_in'] = True  # This is the "Key" to the dashboard
        return jsonify({"success": True}), 200
    
    return jsonify({"success": False}), 401