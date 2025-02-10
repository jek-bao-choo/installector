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

        print("***DEBUG self.message_history.append: ", self.message_history)

    def _format_prompt(self) -> List[Dict[str, str]]:
        """Format the message history with a prompt template"""
        # Define the base prompt template that sets the AI's role and behavior
        base_prompt = {
            "role": "system",
            "content": """You are an AI assistant specialized in Kubernetes and cloud-native technologies. 
Your primary focus is helping users with installation, configuration, and troubleshooting of cloud-native tools and applications.

Follow these guidelines:
- Provide clear, step-by-step instructions
- Include relevant command examples when appropriate
- Explain potential risks or considerations
- If you're unsure about something, acknowledge it
- Keep responses focused and practical

When suggesting commands or configurations:
- Always explain what each command does
- Highlight any required prerequisites
- Mention any necessary permissions or security considerations"""
        }

        # Start with the base prompt
        formatted_messages = [base_prompt]

        # Add any existing system messages (like system context) after the base prompt
        # Then add user-assistant interactions
        for message in self.message_history:
            if message["role"] == "system" and message not in formatted_messages:
                formatted_messages.append(message)
            elif message["role"] in ["user", "assistant"]:
                formatted_messages.append(message)

        return formatted_messages
    
    def get_response(self) -> Generator[str, None, None]:
        """Get streaming response from LLM"""
        if not self.message_history:
            raise MessageBrokerError("No messages in history to generate response from")
        
        # Format messages with prompt template before sending to LLM
        formatted_messages = self._format_prompt()
        print("***DEBUG get_llm_response: ", formatted_messages)
        return get_llm_response(formatted_messages)
