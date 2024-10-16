
from api.vendor.openai.main import OpenAIStrategy
from api.vendor.claude.main import ClaudeStrategy

def get_strategy(vendor: str) -> 'AIStrategy':
    if vendor.lower() == "openai":
        return OpenAIStrategy()
    elif vendor.lower() == "claude":
        return ClaudeStrategy()
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")
    
