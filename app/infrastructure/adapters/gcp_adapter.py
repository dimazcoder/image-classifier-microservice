import os
import logging
from google.cloud import storage


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/sa-key.json"


class GCPAdapter:
    def __init__(self):
        self.client = storage.Client()

    async def download_file(self, cloud_bucket, destination_path):
        try:
            bucket_name = cloud_bucket['bucket_name']
            bucket_path = cloud_bucket['bucket_path']
            file_name = cloud_bucket['file_name']

            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(bucket_path)

            local_file_path = os.path.join(destination_path, file_name)

            blob.download_to_filename(local_file_path)
            logging.info(f"Downloaded {file_name} to {local_file_path}")
            return local_file_path
        except Exception as e:
            logging.error(f"Failed to download file from GCS: {e}")
            return None

    async def upload_file(self, bucket_name, local_filepath, cloud_filepath=None):
        try:
            bucket = self.client.bucket(bucket_name)
            if not cloud_filepath:
                cloud_filepath = os.path.basename(local_filepath)

            blob = bucket.blob(cloud_filepath)
            blob.upload_from_filename(local_filepath)
            logging.info(f"Uploaded file to GCS: {bucket_name}/{cloud_filepath}")
            return self.get_url(bucket_name, cloud_filepath)
        except Exception as e:
            logging.error(f"Failed to upload file to GCS: {e}")

    def get_url(self, bucket_name, cloud_filepath):
        logging.info(f"Getting URL for file in GCS: {bucket_name}/{cloud_filepath}")
        return f"https://storage.googleapis.com/{bucket_name}/{cloud_filepath}"
