from typing import List, Dict, Optional

class PromptGenerationError(Exception):
    """Base exception for prompt generation errors"""
    pass

def format_system_info(system_info: Optional[Dict] = None) -> str:
    """Format system information into a readable string"""
    try:
        if not system_info:
            return "No system information available"

        system_details = []
        
        # Extract OS info
        if os_info := system_info.get('os_info', {}):
            try:
                system = os_info.get('system', 'Unknown')
                version = os_info.get('version', 'Unknown')
                distro = os_info.get('distro', 'Unknown')
                system_details.append(f"OS: {system} (Version: {version})")
                if distro != 'Unknown':
                    system_details.append(f"Distribution: {distro}")
            except Exception as e:
                raise PromptGenerationError(f"Error formatting OS info: {str(e)}")

        # Extract Terminal info
        if terminal_info := system_info.get('terminal_info', {}):
            try:
                term_type = terminal_info.get('terminal_type', 'Unknown')
                term_program = terminal_info.get('terminal_program', 'Unknown')
                term_version = terminal_info.get('terminal_version', 'Unknown')
                system_details.append(f"Terminal: {term_type} (Program: {term_program}, Version: {term_version})")
            except Exception as e:
                raise PromptGenerationError(f"Error formatting terminal info: {str(e)}")

        # Extract Kubernetes info
        if k8s_info := system_info.get('kubernetes_info', {}):
            try:
                k8s_status = 'Available' if k8s_info.get('kubectl_available') else 'Not Available'
                k8s_version = k8s_info.get('kubectl_version', 'N/A')
                helm_status = 'Available' if k8s_info.get('helm_available') else 'Not Available'
                helm_version = k8s_info.get('helm_version', 'N/A')
                system_details.append(f"Kubernetes: {k8s_status} (Version: {k8s_version})")
                system_details.append(f"Helm: {helm_status} (Version: {helm_version})")
            except Exception as e:
                raise PromptGenerationError(f"Error formatting Kubernetes info: {str(e)}")

        return '\n'.join(system_details)
    except Exception as e:
        raise PromptGenerationError(f"Error processing system information: {str(e)}")

def format_prompt(message_history: List[Dict[str, str]], system_info: Optional[Dict] = None) -> List[Dict[str, str]]:
    """Format the message history with a prompt template"""
    
    try:
        # Validate message history
        if not isinstance(message_history, list):
            raise PromptGenerationError("Message history must be a list")
        
        for message in message_history:
            if not isinstance(message, dict) or 'role' not in message or 'content' not in message:
                raise PromptGenerationError("Invalid message format in history")

        # Get formatted system information
        system_context = format_system_info(system_info)

        # Define the base prompt template
        base_prompt = {
            "role": "system",
            "content": f"""You are a DevOps Engineer.
Your primary focus is to guide me on installing OpenTelemetry agents according to my operating systems information.

Follow these guidelines:
- Explain potential risks or considerations
- If you're unsure about something, acknowledge it
- Keep responses focused and practical

When suggesting commands or configurations:
- Always explain what each command does
- Highlight any required prerequisites
- Mention any necessary permissions or security considerations

Operating System information:
{system_context}

Based on this information:
- Recommend appropriate OpenTelemetry installation methods
- Suggest specific configurations for the detected environment
- Consider any detected Kubernetes/Helm setup for deployment options
- Adapt instructions to the specific OS and distribution"""
        }

        # Start with the base prompt and user-assistant interactions
        formatted_messages = [base_prompt] + [
            msg for msg in message_history 
            if msg["role"] in ["user", "assistant"]
        ]

        # Validate final formatted messages
        if not formatted_messages:
            raise PromptGenerationError("No valid messages generated")

        return formatted_messages

    except PromptGenerationError as e:
        raise e
    except Exception as e:
        raise PromptGenerationError(f"Unexpected error in prompt generation: {str(e)}")
