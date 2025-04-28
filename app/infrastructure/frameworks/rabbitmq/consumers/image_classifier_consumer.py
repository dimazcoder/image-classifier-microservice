import json
import logging
import traceback
from pydantic import ValidationError

from app.core.dependency import get_property_controller
from app.infrastructure.frameworks.rabbitmq.consumer import RabbitMQConsumer
from app.schemas.property_schema import PropertyImagesSchema


class ImageClassifierConsumer(RabbitMQConsumer):
    async def callback(self, message):
        logging.info(f"Message received from image classifier with body: {message}")

        try:
            message_dict = json.loads(message)
            property_images = PropertyImagesSchema(**message_dict)
            controller = get_property_controller()

            await controller.process_property_om_images(
                property_images
            )
        except (json.JSONDecodeError, ValidationError) as e:
            logging.error(f"Error decoding or validating message: {e}")
        except Exception as e:
            traceback_str = traceback.format_exc()
            logging.error(f"Error processing property data: {traceback_str}")


