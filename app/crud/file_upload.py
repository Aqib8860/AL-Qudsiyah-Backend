import os
import boto3
from dotenv import load_dotenv

from fastapi import HTTPException


load_dotenv()


access_key = os.environ.get("ACCESS_KEY")
bucket_name = os.environ.get("BUCKET_NAME")
secret_key = os.environ.get("SECRET_KEY")
aws_url = os.environ.get("AWS_URL")

def upload_to_s3(file, file_name, content_type):

    file_url = f"media/{file_name}"
    file_url = file_url.replace(" ", "")

    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    try:

        s3.upload_fileobj(file, bucket_name, file_url,
                            ExtraArgs={
                                "ContentType": content_type,
                                'ACL': 'public-read'
                            })
        # Construct the URL of the uploaded file
        image_url = f"{aws_url}/{file_url}"

        return image_url

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"AWS error: {e}")

