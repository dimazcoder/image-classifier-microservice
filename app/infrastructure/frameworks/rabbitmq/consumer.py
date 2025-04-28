class RabbitMQConsumer:
    def callback(self, message):
        raise NotImplementedError("Callback method should be implemented in subclasses")
