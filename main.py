from flask import Flask, redirect, request, jsonify, session, render_template, url_for
# from clerk_backend_api import jwt
import os
from dotenv import load_dotenv
load_dotenv()
from app.auth import require_auth
import jwt
app = Flask(__name__)

# Fallback keys are used for development, but it will prioritize your .env file
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Make sure you add CLERK_JWKS_URL to your .env file
# It looks like: https://your-slug.clerk.accounts.dev/.well-known/jwks.json
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

from clerk_backend_api import authenticate_request, AuthenticateRequestOptions

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

if __name__ == '__main__':
    app.run(debug=True)