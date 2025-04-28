import logging

import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException

from app.core.config import config


class S3Adapter:
    def __init__(self):
        self.client = None

    def connect(self) -> None:
        if not self.client:
            self.client = boto3.client(
                's3',
                aws_access_key_id=config.s3_access_key,
                aws_secret_access_key=config.s3_secret_key
            )

    def upload_file(self, bucket_name, local_filepath, cloud_filepath=None):
        if not cloud_filepath:
            cloud_filepath = local_filepath.split('/')[-1]

        logging.info(f"Uploading file to S3: {bucket_name}/{cloud_filepath}")
        try:
            self.connect()
            self.client.upload_file(local_filepath, bucket_name, cloud_filepath)
            return self.get_url(bucket_name, cloud_filepath)
            # return f"https://{bucket_name}.s3.amazonaws.com/{cloud_filename}"
        except NoCredentialsError:
            return "AWS credentials not found. Ensure you have set up your AWS credentials properly."
        except Exception as e:
            raise HTTPException(status_code=500, detail="Unable to upload file to S3 bucket")

    def download_file(self, bucket_name, cloud_filepath, local_filepath):
        logging.info(f"Downloading file from S3: {bucket_name}/{cloud_filepath} to {local_filepath}")
        try:
            self.connect()
            self.client.download_file(bucket_name, cloud_filepath, local_filepath)
        except Exception as e:
            logging.error(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Unable to download file from S3 bucket")

    def get_url(self, bucket_name, cloud_filepath):
        return f"https://{bucket_name}.s3.amazonaws.com/{cloud_filepath}"
