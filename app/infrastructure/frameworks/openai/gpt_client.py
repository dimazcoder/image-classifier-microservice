from openai import OpenAI
from app.core.config import config


class GPTClient:
    def __init__(self):
        self.client = None
        self.openai_api_key = config.openai_api_key

    def get_client(self):
        if self.client is None:
            self.client = OpenAI(api_key=self.openai_api_key)
        return self.client

    def connect_client(self):
        self.client = OpenAI(api_key=self.openai_api_key)
