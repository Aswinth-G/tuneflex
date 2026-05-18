import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', 'your-cloud-name'),
    api_key = os.getenv('CLOUDINARY_API_KEY', 'your-api-key'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET', 'your-api-secret'),
    secure = True
)

try:
    result = cloudinary.api.resources(
        type="upload",
        prefix="tuneflex/audio/",
        resource_type="video",  
        max_results=500  
    )
    resources = result['resources']
    print(f"Total songs stored in Cloudinary: {len(resources)}")
    print("Song names:")
    for res in resources:
        # Extract filename from public_id
        filename = res['public_id'].split('/')[-1]
        print(f"- {filename}")
except Exception as e:
    print(f"Error: {e}")