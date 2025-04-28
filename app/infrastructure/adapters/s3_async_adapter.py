import logging
import traceback

from aiobotocore.session import get_session
from botocore.exceptions import NoCredentialsError
from app.core.config import config


class S3AsyncAdapter:
    def __init__(self):
        self.client = None

    async def connect(self):
        if not self.client:
            session = get_session()
            self.client = session.create_client(
                's3',
                aws_access_key_id=config.s3_access_key,
                aws_secret_access_key=config.s3_secret_key
            )

    async def create_client(self):
        session = get_session()
        return session.create_client(
            's3',
            aws_access_key_id=config.s3_access_key,
            aws_secret_access_key=config.s3_secret_key
        )

    async def close(self):
        if self.client:
            await self.client.close()

    async def upload_file(self, bucket_name, local_filepath, cloud_filepath=None):
        if not cloud_filepath:
            cloud_filepath = local_filepath.split('/')[-1]

        logging.info(f"Uploading file to S3: {bucket_name}/{cloud_filepath}")
        try:
            async with await self.create_client() as s3_client:
                # await s3_client.upload_file(local_filepath, bucket_name, cloud_filepath)
                with open(local_filepath, 'rb') as data:
                    await s3_client.put_object(Bucket=bucket_name, Key=cloud_filepath, Body=data)
            return self.get_url(bucket_name, cloud_filepath)
        except NoCredentialsError:
            return "AWS credentials not found. Ensure you have set up your AWS credentials properly."
        except Exception as e:
            traceback_str = traceback.format_exc()
            logging.error(f"Error: {traceback_str}")

    async def download_file(self, bucket_name, cloud_filepath, local_filepath):
        logging.info(f"Downloading file from S3: {bucket_name}/{cloud_filepath} to {local_filepath}")
        try:
            await self.connect()
            async with self.client as s3_client:
                response = await s3_client.get_object(Bucket=bucket_name, Key=cloud_filepath)
                async with response['Body'] as stream:
                    with open(local_filepath, 'wb') as f:
                        chunk = await stream.read()
                        f.write(chunk)
        except Exception as e:
            logging.error(f"Error: {e}")

    def get_url(self, bucket_name, cloud_filepath):
        return f"https://{bucket_name}.s3.amazonaws.com/{cloud_filepath}"
