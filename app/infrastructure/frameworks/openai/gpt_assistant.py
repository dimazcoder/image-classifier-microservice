from app.infrastructure.frameworks.openai.gpt_client import GPTClient


class GPTAssistant(GPTClient):
    def __init__(self):
        super().__init__()
        self.assistant = self.create_assistant()
        self.vector_store = None

    def create_assistant(self):
        raise NotImplementedError

    def upload_file(self, file):
        if not self.assistant:
            raise ValueError("Assistant not defined")

        self.vector_store = self.client.beta.vector_stores.create(name=self.assistant.name)

        self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id, files=[file]
        )

        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store.id]}},
        )

    def clear(self):
        self.client.beta.vector_stores.delete(
            vector_store_id= self.vector_store.id
        )

        self.client.beta.assistants.delete(
            self.assistant.id
        )

