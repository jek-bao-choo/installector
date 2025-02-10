from typing import List, Dict

def format_prompt(message_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Format the message history with a prompt template"""
    # Define the base prompt template that sets the AI's role and behavior
    base_prompt = {
        "role": "system",
        "content": """You are a DevOps Engineer.
Your primary focus is guide me on installing OpenTelemetry agents according to my operating systems information.

Follow these guidelines:
- Explain potential risks or considerations
- If you're unsure about something, acknowledge it
- Keep responses focused and practical

When suggesting commands or configurations:
- Always explain what each command does
- Highlight any required prerequisites
- Mention any necessary permissions or security considerations

Operating System information:"""
    }

    # Start with the base prompt
    formatted_messages = [base_prompt]

    # Add any existing system messages (like system context) after the base prompt
    # Then add user-assistant interactions
    for message in message_history:
        if message["role"] == "system" and message not in formatted_messages:
            formatted_messages.append(message)
        elif message["role"] in ["user", "assistant"]:
            formatted_messages.append(message)

    return formatted_messages
