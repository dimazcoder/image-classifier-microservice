from app.infrastructure.frameworks.openai.gpt_assistant import GPTAssistant


class RealpageAssistant(GPTAssistant):
    def __init__(self):
        super().__init__()

    def create_assistant(self):
        self.get_client()
        return self.client.beta.assistants.create(
            name="Assistant",
            instructions="You are an expert in real estate analytical data. Use you knowledge base to answer questions about real estate analytics based on uploaded files.",
            model="gpt-4-turbo",
            temperature=0.1,
            tools=[{"type": "file_search"}],
        )
