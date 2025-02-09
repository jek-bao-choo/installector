# Import necessary types and the LLM response function
from typing import Generator, List, Dict
from server.llm import get_llm_response

# Define MessageBroker class to manage conversation history and LLM interaction
class MessageBroker:
    def __init__(self):
        # Initialize an empty list to store conversation history
        self.message_history: List[Dict[str, str]] = []
    
    def add_message(self, content: str, role: str = "user") -> None:
        """Add a message to the conversation history"""
        # Append a new message dictionary to the history
        self.message_history.append({
            "role": role,        # Who sent the message (user/assistant)
            "content": content   # The actual message content
        })
    
    def get_response(self) -> Generator[str, None, None]:
        """Get streaming response from LLM"""
        # Forward the message history to the LLM and return its response stream
        return get_llm_response(self.message_history)
