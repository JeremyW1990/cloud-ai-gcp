from abc import ABC, abstractmethod
from api.vendor.vendor_strategy import AIStrategy
from api.vendor.openai.main import OpenAIStrategy
from api.vendor.claude.main import ClaudeStrategy

def get_strategy(vendor: str) -> AIStrategy:
    if vendor.lower() == "openai":
        return OpenAIStrategy()
    elif vendor.lower() == "claude":
        return ClaudeStrategy()
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")
    
class AIStrategy(ABC):
    @abstractmethod
    def initialize_client(self, api_key):
        pass

    @abstractmethod
    def init_assistant(self, name, instruction):
        pass

    @abstractmethod
    def create_thread_with_context(self, context):
        pass

    @abstractmethod
    def create_thread_and_run(self, assistant_id, user_input):
        pass

    @abstractmethod
    def submit_message(self, assistant_id, thread, user_message):
        pass

    @abstractmethod
    def wait_on_run(self, run, thread):
        pass

    @abstractmethod
    def get_response(self, thread):
        pass

    @abstractmethod
    def get_latest_response(self, messages):
        pass

    @abstractmethod
    def extract_next_agent(self, message):
        pass

    @abstractmethod
    def extract_current_agent(self, message):
        pass
