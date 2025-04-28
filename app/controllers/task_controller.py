import json
import logging

from app.schemas.property_schema import PropertySchema
from app.schemas.task_schema import TaskSchema
from app.services.queue_service import QueueService


class TaskController:
    def __init__(self):
        pass

    async def send_test(self, property_data: PropertySchema):
        service = QueueService()
        message = property_data.json()
        await service.send_message(
            'pdf_image_processing_tasks', message
        )

    def handle_task(self, task_data: TaskSchema):
        pass

    def register_task(self, task_data: TaskSchema) -> str:
        pass

    async def add_pdf_image_processing_task(self, property_data: PropertySchema):
        service = QueueService()
        message = property_data.json()
        logging.info(f"Message from API Call {message}")
        await service.send_message(
            'pdf_image_processing_tasks', message
        )
