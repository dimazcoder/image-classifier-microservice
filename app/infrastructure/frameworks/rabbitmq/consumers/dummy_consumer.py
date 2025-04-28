import logging

from app.infrastructure.frameworks.rabbitmq.consumer import RabbitMQConsumer


class DummyConsumer(RabbitMQConsumer):
    def __init__(self, channel=None):
        super().__init__(channel)

    def callback(self, message):
        logging.info(f"Message received with body: {message}")

