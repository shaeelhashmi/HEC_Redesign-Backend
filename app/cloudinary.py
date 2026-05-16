import cloudinary
import cloudinary.uploader
from .config import Config

# Apply the configuration from your config file
cloudinary.config(**Config.CLOUDINARY_CONFIG)
def upload_to_cloudinary(file_to_upload):
    """
    Takes a file object and returns the cloudinary upload result.
    """
    if file_to_upload:
        try:
            # Upload the file
            upload_result = cloudinary.uploader.upload(file_to_upload)
            return upload_result
        except Exception as e:
            print(f"Cloudinary error: {e}")
            return None
    return None