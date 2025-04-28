import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Config(BaseModel):
    env: str = os.getenv("ENV", "dev")

    api_url: str = "/api"
    api_v1_url: str = api_url + "/v1"
    api_key: str = os.getenv("API_KEY", "")

    project_title: str = "Image Extractor"
    project_version: str = "0.0.1"

    datetime_format: str = "%Y-%m-%dT%H:%M:%S"
    date_format: str = "%Y-%m-%d"

    cors_origins: List[str] = ['*']

    default_db: str = os.getenv("OM_DB", "OM-DEV")

    mongo_uri: str = os.getenv("MONGO_URI","")
    s3_pdf_bucket: str = os.getenv("S3_PDF_BUCKET", "")
    s3_image_bucket: str = os.getenv("S3_IMAGE_BUCKET", "")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "")
    s3_region: str = os.getenv("S3_REGION", "us-west-2")

    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "")
    rabbitmq_virtual_host: str = os.getenv("RABBITMQ_VIRTUAL_HOST", "")
    rabbitmq_username: str = os.getenv("RABBITMQ_USERNAME", "")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "")
    rabbitmq_routing_key: str = os.getenv("RABBITMQ_ROUTING_KEY", "")

    socket_uri: str = os.getenv("SOCKET_URI", "")

    project_root: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    static_path: str = os.path.join(project_root, 'static')
    downloads_path: str = os.path.join(static_path, 'downloads')
    pdf_images_path: str = os.path.join(static_path, 'pdf_images')
    classifier_path: str = os.path.join(static_path, 'classifier')

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")


config = Config()
