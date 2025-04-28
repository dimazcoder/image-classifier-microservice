from app.core.config import config
from app.infrastructure.adapters.socket_adapter import SocketAdapter


class MessengerService:
    def __init__(self):
        self.adapter = SocketAdapter()

    def send_message(self, message, data):
        self.adapter.connect(config.socket_uri)
        print(f"Sending message {message} {data}", flush=True)
        self.adapter.send_message(
            message,
            data
        )
        self.adapter.disconnect()
