import logging

from app.core.config import config
from app.infrastructure.adapters.rabbit_async_adapter import RabbitMQAsyncAdapter

import asyncio

class QueueService:
    def __init__(self, rabbitmq_url=None):
        rabbitmq_url = rabbitmq_url if rabbitmq_url else f"amqp://{config.rabbitmq_username}:{config.rabbitmq_password}@{config.rabbitmq_host}/{config.rabbitmq_virtual_host}"
        self.adapter = RabbitMQAsyncAdapter(rabbitmq_url)
        self.routing_key = config.rabbitmq_routing_key
        self.consumers = {}

    async def send_message(self, queue_name, message):
        await self.adapter.send_message(queue_name, message)

    async def send_direct_message(self, queue_name, message, routing_key=None):
        routing_key = routing_key if routing_key else self.routing_key
        await self.adapter.send_message(queue_name, message, routing_key)

    def bind_consumer(self, queue_name, handler):
        self.consumers[queue_name] = handler

    def bind_direct_consumer(self, queue_name, handler, routing_key=None):
        queue_name = self.prep_queue_name(queue_name, routing_key)
        self.consumers[queue_name] = handler

    async def run_consumers(self):
        while True:
            if not self.adapter.connection or self.adapter.connection.is_closed:
                logging.info('Queue Service connection is closed...')
                await self.adapter.connect()
                await self.start_consumers()

    async def start_consumers(self):
        for queue_name, consumer in self.consumers.items():
            asyncio.create_task(self.run_consumer(queue_name, consumer))
        logging.info('Start consuming...')

    async def run_consumer(self, queue_name, consumer_class):
        consumer = consumer_class()
        # logging.info(f"run_consumer: {queue_name} {consumer_class.__name__}")
        while True:
            await self.consume_queue(queue_name, consumer.callback)

    async def consume_queue(self, queue_name, message_handler):
        # logging.info(f"consume_queue: {queue_name} {message_handler}")
        await self.adapter.connect()
        await self.adapter.declare_queue(queue_name)
        await self.adapter.consume_messages(queue_name, lambda message: self.consume_message(message, message_handler))
        await asyncio.Future()

    async def consume_message(self, message, message_handler):
        async with message.process():
            await message_handler(message.body.decode('utf-8') if isinstance(message.body, bytes) else message.body)

    def prep_queue_name(self, queue_name, routing_key=None):
        routing_key = routing_key if routing_key else self.routing_key
        return f"{queue_name}_{routing_key}" if routing_key else queue_name

    async def health_check(self):
        while True:
            try:
                if not self.adapter.connection or self.adapter.connection.is_closed:
                    logging.warning("Connection is closed. Reconnecting...")
                    await self.adapter.connect()
                    await self.start_consumers()
            except Exception as e:
                logging.error(f"Health check error: {e}")
            await asyncio.sleep(10)  # Check every 10 seconds
