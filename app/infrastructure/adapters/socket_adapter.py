import socketio
from fastapi import HTTPException

class SocketAdapter:
    def __init__(self):
        self.client = None

    def connect(self, uri):
        if not self.client:
            self.client = socketio.Client()

        try:
            self.client.connect(uri)
        except socketio.exceptions.ConnectionError:
            raise HTTPException(status_code=500, detail="Unable to connect with socket")

    def disconnect(self):
        self.client.disconnect()

    def send_message(self, message, data=None):
        self.client.emit(message, data)
        self.client.sleep(0.25)

