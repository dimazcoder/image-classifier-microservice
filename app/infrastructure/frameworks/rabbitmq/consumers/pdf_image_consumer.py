import json
import logging
import traceback

from app.core.dependency import get_property_controller
from app.infrastructure.frameworks.rabbitmq.consumer import RabbitMQConsumer
from app.schemas.property_schema import PropertySchema
from pydantic import ValidationError

class PdfImageConsumer(RabbitMQConsumer):
    async def callback(self, payload):
        try:
            payload_dict = json.loads(payload)
            property_data = PropertySchema(**payload_dict)
            controller = get_property_controller()

            await controller.extract_images_from_property_om(
                property_data
            )
        except (json.JSONDecodeError, ValidationError) as e:
            logging.error(f"Error decoding or validating message: {e}")
        except Exception as e:
            traceback_str = traceback.format_exc()
            logging.error(f"Error processing property data: {traceback_str}")
