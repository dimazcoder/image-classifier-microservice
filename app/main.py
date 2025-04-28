import asyncio
import logging
import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.middlewares.auth_middleware import check_api_key
from app.api.v1.routes import routers as v1_routers
from app.api.routes import router as routers
from app.core.config import Config
from app.services.queue_service import QueueService


class AppFactory():
    def __init__(self, config: Config) -> None:
        self.config = config

        logging.basicConfig(level=logging.INFO)

        self.app = FastAPI(
            title=self.config.project_title,
            version=self.config.project_version,
            openapi_url=f"/openapi.json"
        )

        self.app.middleware("http")(check_api_key)

        if self.config.cors_origins:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in self.config.cors_origins],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["X-Process-Time"],
            )

        self.app.include_router(routers)
        self.app.include_router(v1_routers, prefix=self.config.api_v1_url)
        self.app.add_event_handler("startup", self.on_startup)

    async def on_startup(self):
        # # 20240705, Dima: commented with implementing queueless
        # await self.start_consumers()

        os.makedirs(self.config.downloads_path, exist_ok=True)
        os.makedirs(self.config.pdf_images_path, exist_ok=True)
        os.makedirs(self.config.classifier_path, exist_ok=True)

    def get_app(self) -> FastAPI:
        return self.app

    async def start_consumers(self):
        from app.infrastructure.frameworks.rabbitmq.consumers.image_classifier_consumer import ImageClassifierConsumer
        from app.infrastructure.frameworks.rabbitmq.consumers.pdf_image_consumer import PdfImageConsumer

        queue_service = QueueService()
        queue_service.bind_direct_consumer('image_classifying_tasks', ImageClassifierConsumer)
        queue_service.bind_consumer('pdf_image_processing_tasks', PdfImageConsumer)
        asyncio.create_task(queue_service.start_consumers())
        asyncio.create_task(queue_service.health_check())


def create_app() -> FastAPI:
    config = Config()
    factory = AppFactory(config)
    return factory.get_app()


app = create_app()
