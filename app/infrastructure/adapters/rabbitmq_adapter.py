import threading
import time
import logging

import pika
import pika.exceptions

from app.core.config import config

class RabbitMQAdapter:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.consumers = None
        self.routing_key = config.rabbitmq_routing_key

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=config.rabbitmq_host,
                    virtual_host=config.rabbitmq_virtual_host,
                    credentials=pika.PlainCredentials(
                        username=config.rabbitmq_username,
                        password=config.rabbitmq_password
                    ),
                    heartbeat=60,
                    # blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()
            logging.info("Connected to RabbitMQ")
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Error connecting to RabbitMQ: {e}")
            self.reconnect()

    def reconnect(self):
        logging.info("Reconnecting to RabbitMQ in 5 seconds...")
        time.sleep(5)
        self.connect()

    def send_message(self, exchange_name, message):
        try:
            if not self.channel or not self.channel.is_open:
                logging.warning("The channel is closed. Reconnecting...")
                self.reconnect()
                return
            self.channel.basic_publish(
                exchange=exchange_name, routing_key=self.routing_key, body=message
            )
            logging.info(f"Sent to {exchange_name} with routing key '{self.routing_key}' message: {message}")
        except pika.exceptions.AMQPError as e:
            logging.error(f"Error sending message: {e}")
            self.reconnect()

    def listen(self, consumers):
        if not consumers:
            return False
        self.consumers = consumers
        self.connect()  # Start connection process in a blocking manner
        listen_thread = threading.Thread(target=self.start_listening)
        listen_thread.daemon = True
        listen_thread.start()

    def start_listening(self):
        try:
            if not self.channel or not self.channel.is_open:
                logging.warning("Attempting to start listening without an open channel. Reconnecting...")
                self.reconnect()
                return
            for queue_name, consumer_class, auto_ack, exclusive in self.get_consumers():
                consumer = consumer_class(self.channel)
                self.channel.basic_qos(prefetch_count=1)  # only one message in a time
                self.channel.basic_consume(
                    queue=queue_name, on_message_callback=consumer.callback, auto_ack=auto_ack, exclusive=exclusive
                )
                self.consumers[queue_name] = consumer
            self.channel.start_consuming()
        except pika.exceptions.AMQPError as e:
            logging.error(f"Error starting message consumption: {e}")
            self.reconnect()

    def get_consumers(self):
        """
        The consumer description in self.consumers can be in one of the following formats:
        {
            'dummy-queue-1': {
                'consumer': DummyConsumer,
                'auto_ack': False,
                'exclusive': True
            },
            'dummy-queue-2': {
                'consumer': DummyConsumer,
            },
            'dummy-queue-3': DummyConsumer
        }
        """
        consumers = []
        for key, value in self.consumers.items():
            queue_name = self.prep_queue_name(key)
            if isinstance(value, dict):
                consumer_class = value['consumer']
                auto_ack = value.get('auto_ack', False)
                exclusive = value.get('exclusive', False)
            else:
                consumer_class = value
                auto_ack = False
                exclusive = True
            consumers.append((queue_name, consumer_class, auto_ack, exclusive))
        return consumers

    def prep_queue_name(self, queue_name):
        return f"{queue_name}_{self.routing_key}"
