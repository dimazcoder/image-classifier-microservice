import logging
import time

from app.infrastructure.frameworks.openai.gpt_client import GPTClient


class GPTAdapter(GPTClient):
    def __init__(self):
        super().__init__()
        self.assistant = None
        self.thread = None
        # self.run = None
        self.max_requests = 10
        self.request_counter = 0
        self.attempts_per_request = 3
        self.pause_after_attempt = 0.1  # in seconds
        self.pause_before_request = 0.1 # in seconds

    def use_assistant(self, assistant):
        self.assistant = assistant

    def check_limiter(self):
        if not self.assistant:
            raise ValueError("Assistant not defined")
        logging.info(f"OpenAI adapter request # : {self.request_counter}")
        if self.request_counter >= self.max_requests:
            self.request_counter = 0

        if self.request_counter == 0:
            self.connect_client()
            self.assistant = self.client.beta.assistants.retrieve(
                self.assistant.id
            )
            self.thread = self.client.beta.threads.create()
            # self.run = self.client.beta.threads.runs.create_and_poll(
            #     thread_id=self.thread.id, assistant_id=self.assistant.id, temperature=0.1
            # )

        self.request_counter += 1
        time.sleep(self.pause_before_request)

    def send_message(self, message):
        self.check_limiter()
        for _ in range(self.attempts_per_request):
            try:
                self.client.beta.threads.messages.create(
                    role="user", content=message, thread_id=self.thread.id
                )
                run = self.client.beta.threads.runs.create_and_poll(
                    thread_id=self.thread.id, assistant_id=self.assistant.id, temperature=0.1
                )
                responses = list(self.client.beta.threads.messages.list(
                    thread_id=self.thread.id, run_id=run.id)
                )
                return responses[-1].content[0].text.value
            except Exception as e:
                logging.info(f"OpenAI send message error: {e}")
                time.sleep(self.pause_after_attempt)

        return "Failed to send message after multiple attempts."

        # Version before 01 May 2024
        # if not self.thread:
        #     self.thread = self.client.beta.threads.create()
        #
        # self.client.beta.threads.messages.create(
        #     role="user", content=message, thread_id=self.thread.id
        # )
        #
        # run = self.client.beta.threads.runs.create_and_poll(
        #     thread_id=self.thread.id, assistant_id=self.assistant.id
        # )
        #
        # responses = list(self.client.beta.threads.messages.list(
        #     thread_id=self.thread.id, run_id=self.run.id)
        # )
        #
        # return responses[-1].content[0].text.value

    def clear(self):
        self.get_client()
        if self.thread:
            self.client.beta.threads.delete(
                self.thread.id
            )
