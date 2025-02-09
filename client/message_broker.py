from typing import Generator, List, Dict
from server.llm import get_llm_response

class MessageBroker:
    def __init__(self):
        self.message_history: List[Dict[str, str]] = []
    
    def add_message(self, content: str, role: str = "user") -> None:
        """Add a message to the conversation history"""
        self.message_history.append({
            "role": role,
            "content": content
        })
    
    def get_response(self) -> Generator[str, None, None]:
        """Get streaming response from LLM"""
        return get_llm_response(self.message_history)
