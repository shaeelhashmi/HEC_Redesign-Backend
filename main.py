from flask import Flask, redirect, request, jsonify, session, render_template, url_for
from app.cloudinary import upload_to_cloudinary
import os
from dotenv import load_dotenv
from flask_mysqldb import MySQL
import MySQLdb.cursors
from app.routes.admin.admin import auth_blueprint
load_dotenv()
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

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
app.register_blueprint(auth_blueprint, url_prefix='/admin')
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))
# Fixed: Explicitly added methods=['POST'] argument

from clerk_backend_api import Clerk, authenticate_request, AuthenticateRequestOptions
@app.route('/signup')
def signup_page():
    return render_template('signup.html')
@app.route('/api/login-session', methods=['POST'])
def login_session():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "No email provided"}), 400
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("SELECT email FROM cnic WHERE email = %s", (email,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO cnic (email) VALUES (%s)", (email,))
            mysql.connection.commit()
            print(f"Created new DB record for {email}")
        else:
            print(f"User {email} already in DB")
    except Exception as e:

        print(f"Database error during login: {e}")
        return jsonify({"error": "DB sync failed"}), 500
    finally:
        cursor.close()

    return jsonify({"ok": True}), 200

@app.route('/dashboard')
def dashboard():
    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=os.getenv("CLERK_SECRET_KEY"),
            # Both URLs must be inside this list within the Options object
            authorized_parties=[
                "http://localhost:5000", 
                "http://127.0.0.1:5000"
            ],
        )
    )
    try:
        email = state.payload.get('email')
    except Exception as e:
        print(f"Error extracting email from token: {e}")
        return redirect(url_for('login_page'))
    if not email:
        return redirect(url_for('login_page'))

    status = "Unverified"
    image_url = None
    cnic_num = None

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT CNIC_image, cnic_number FROM cnic WHERE email = %s", (email,))
    record = cursor.fetchone()
    cursor.close()

    if record:
        image_url = record.get('CNIC_image')
        cnic_num = record.get('cnic_number')

        if image_url and not cnic_num:
            status = "Under Review"
        elif image_url and cnic_num:
            status = "CNIC Verified"

    # Pass everything to your index.html
    return render_template('index.html', status=status)

@app.route('/sso-callback')
def sso_callback():
    return render_template('sso_callback.html')
@app.route('/login')
def login_page():
    return render_template('login.html')
clerk_client = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

@app.route('/api/verify-cnic', methods=['POST'])
def verify_cnic():
    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=os.getenv("CLERK_SECRET_KEY"),
            # Both URLs must be inside this list within the Options object
            authorized_parties=[
                "http://localhost:5000", 
                "http://127.0.0.1:5000"
            ],
        )
    )
    print(state)
    if not state.is_signed_in:
        # (Keep your error handling here)
        return jsonify({"error": "Unauthorized"}), 401

    # Check for the correct key: 'cnic_image'
    if 'cnic_image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image_file = request.files['cnic_image']

    
    result = upload_to_cloudinary(image_file)

    if result:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # GET THE URL HERE - This is what you'll save to your SQL table later
        secure_url = result.get('secure_url')
        cursor.execute("UPDATE cnic SET CNIC_image = %s WHERE email = %s", (secure_url, state.payload.get('email')))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "status": "success",
            "url": secure_url,
            "public_id": result.get('public_id')
        }), 200
    else:
        return jsonify({"error": "Upload failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)