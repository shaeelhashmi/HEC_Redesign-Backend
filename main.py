from flask import Flask, redirect, request, jsonify, session, render_template, url_for
from app.cloudinary import upload_to_cloudinary
import os
from dotenv import load_dotenv
load_dotenv()
from app.auth import require_auth
app = Flask(__name__)


app.secret_key = os.getenv("FLASK_SECRET_KEY")

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))
# Fixed: Explicitly added methods=['POST'] argument
@app.route('/protected', methods=['GET'])
@require_auth
def protected():
    return jsonify({"message": "This is a protected route", "user_id": request.user})

from clerk_backend_api import Clerk, authenticate_request, AuthenticateRequestOptions

@app.route('/api/login-session', methods=['GET'])
def login_session():
    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=os.getenv("CLERK_SECRET_KEY"),
            jwt_key=os.getenv("CLERK_JWT_KEY"),  # the JWKS public key PEM
            authorized_parties=["http://127.0.0.1:5000"],
            accepts_token=["session_token"],
        )
    )

    if not state.is_signed_in:
        return jsonify({"error": state.reason or "unauthorized"}), 401

    clerk_user_id = state.payload["sub"]
    session["user_id"] = clerk_user_id

    return jsonify({"ok": True, "user_id": clerk_user_id}), 200

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')
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
    if not state.is_signed_in:
        # (Keep your error handling here)
        return jsonify({"error": "Unauthorized"}), 401

    # Check for the correct key: 'cnic_image'
    if 'cnic_image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image_file = request.files['cnic_image']


    result = upload_to_cloudinary(image_file)

    if result:
        # GET THE URL HERE - This is what you'll save to your SQL table later
        secure_url = result.get('secure_url')
        
        return jsonify({
            "status": "success",
            "url": secure_url,
            "public_id": result.get('public_id')
        }), 200
    else:
        return jsonify({"error": "Upload failed"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)