from api.vendor.base_strategy import AIStrategy


class ClaudeStrategy(AIStrategy):
    def __init__(self):
        self.client = None

    def initialize_client(self, api_key):
        pass
    
 