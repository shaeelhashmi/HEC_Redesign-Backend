from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
    CLERK_JWT_KEY = os.getenv("CLERK_JWT_KEY")
    
    # Cloudinary Specific
    CLOUDINARY_CONFIG = {
        'cloud_name': os.getenv('CLOUD_NAME'),
        'api_key': os.getenv('API_KEY'),
        'api_secret': os.getenv('API_SECRET'),
        'secure': True
    }