from typing import Annotated

import clerk
from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
from clerk_backend_api.security.types import RequestState
from flask import request

def require_auth(func):
    def wrapper(*args, **kwargs):
        # Create a RequestState object to hold the authentication state
        auth_header=request.headers.get("Authorization")
        if not auth_header:
            return {"error": "Authorization header missing"}, 401
        token = auth_header.split(" ")[1] if " " in auth_header else None
        try:
            sessions=clerk.sessions.verify_session(token)
            request.user=sessions["user_id"]
            return func(*args, **kwargs)
        except Exception as e:
            return {"error": f"Unauthorized: {str(e)}"}, 401
    wrapper.__name__ = func.__name__
    return wrapper
