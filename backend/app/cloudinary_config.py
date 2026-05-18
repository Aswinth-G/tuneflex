import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

def configure_cloudinary():
    
    cloudinary.config(
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', 'your-cloud-name'),
        api_key = os.getenv('CLOUDINARY_API_KEY', 'your-api-key'),
        api_secret = os.getenv('CLOUDINARY_API_SECRET', 'your-api-secret'),
        secure = True
    )

try:
    configure_cloudinary()
    print("Cloudinary configured successfully")
except Exception as e:
    print(f"Cloudinary configuration error: {e}")

def upload_audio_to_cloudinary(local_path: str, folder: str = "tuneflex/audio") -> str:
    """
    Upload audio file to Cloudinary and return the URL
    
    Args:
        local_path: Path to the local audio file
        folder: Cloudinary folder to store the file
        
    Returns:
        str: Public URL of the uploaded file
    """
    try:
        # Upload file to Cloudinary
        response = cloudinary.uploader.upload(
            local_path,
            resource_type = "video",  # Use "video" for audio files
            folder = folder,
            format = "mp3",  # Convert to mp3 if needed
            use_filename = True,  # Use original filename
            unique_filename = True,  # Add random suffix to avoid conflicts
            overwrite = False
        )
        
        print(f"File uploaded to Cloudinary: {response['public_id']}")
        print(f"Public URL: {response['secure_url']}")
        
        return response['secure_url']
        
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        raise e

def delete_from_cloudinary(public_url: str) -> bool:
    """
    Delete file from Cloudinary using its public URL
    
    Args:
        public_url: Public URL of the file to delete
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/cloud_name/video/upload/filename
        if "cloudinary.com" in public_url:
            parts = public_url.split('/')
            if len(parts) >= 8:
                # Get the last part (filename) and remove extension
                filename = parts[-1].split('.')[0]
                public_id = f"tuneflex/audio/{filename}"
                
                # Delete from Cloudinary
                response = cloudinary.uploader.destroy(public_id, resource_type="video")
                print(f"File deleted from Cloudinary: {public_id}")
                return response.get('result') == 'ok'
        
        return False
        
    except Exception as e:
        print(f"Error deleting from Cloudinary: {e}")
        return False
