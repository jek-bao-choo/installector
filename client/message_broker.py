from typing import Generator, List, Dict, Optional
from server.llm import get_llm_response

class MessageBrokerError(Exception):
    """Base exception class for MessageBroker errors"""
    pass

# Define MessageBroker class to manage conversation history and LLM interaction
class MessageBroker:
    def __init__(self, max_history: int = 100):
        self.message_history: List[Dict[str, str]] = []
        self.max_history = max_history
    
    def add_message(self, content: str, role: str = "user") -> None:
        """Add a message to the conversation history"""
        if not content or not isinstance(content, str):
            raise MessageBrokerError("Message content must be a non-empty string")
        if role not in ["user", "assistant", "system"]:
            raise MessageBrokerError("Invalid role. Must be 'user', 'assistant', or 'system'")
            
        if len(self.message_history) >= self.max_history:
            self.message_history.pop(0)  # Remove oldest message if limit reached
            
        self.message_history.append({
            "role": role,
            "content": content
        })
    
    def get_response(self) -> Generator[str, None, None]:
        """Get streaming response from LLM"""
        if not self.message_history:
            raise MessageBrokerError("No messages in history to generate response from")
        return get_llm_response(self.message_history)
