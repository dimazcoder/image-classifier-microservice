import logging
import aio_pika
import asyncio


class RabbitMQAsyncAdapter:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.heartbeat = 60
        self.connection = None
        self.channel = None
        self.reconnect_delay = 5  # sec

    async def connect(self):
        if self.connection is None or self.connection.is_closed:
            while True:
                try:
                    self.connection = await aio_pika.connect_robust(
                        self.amqp_url,
                        heartbeat=self.heartbeat,
                    )
                    self.channel = await self.connection.channel()
                    logging.info("Connected to RabbitMQ")
                    break
                except (aio_pika.exceptions.AMQPConnectionError, ConnectionError) as e:
                    logging.info(f"Failed to connect to RabbitMQ: {e}")
                    logging.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                    await asyncio.sleep(self.reconnect_delay)

    # async def declare_exchange(self, exchange_name, exchange_type='direct'):
    #     await self.connect()
    #     return await self.channel.declare_exchange(exchange_name, exchange_type=exchange_type)

    async def declare_queue(self, queue_name, durable=True):
        await self.connect()
        return await self.channel.declare_queue(queue_name, durable=durable)

    async def get_exchange(self, exchange_name: str):
        await self.connect()
        return await self.channel.get_exchange(exchange_name)

    async def send_message(self, exchange_name: str, message_body: str, routing_key: str = ""):
        await self.connect()
        exchange = await self.get_exchange(exchange_name)
        message = aio_pika.Message(body=message_body.encode())
        await exchange.publish(message, routing_key=routing_key)
        logging.info(f"Message published to exchange '{exchange_name}' with routing key '{routing_key}' body: {message_body}")

    async def consume_messages(self, queue_name, message_handler):
        await self.connect()
        queue = await self.declare_queue(queue_name)
        await queue.consume(message_handler)

    async def acknowledge_message(self, message):
        if message and not message.processed:
            await message.ack()

    async def reject_message(self, message, requeue=False):
        if message and not message.processed:
            await message.reject(requeue=requeue)

    async def close(self):
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
