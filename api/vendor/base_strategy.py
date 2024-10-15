from abc import ABC, abstractmethod
    
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
