from typing import List, Dict, Optional, Tuple
from server.obs_base_prompt import get_base_prompt

class PromptGenerationError(Exception):
    """Base exception for prompt generation errors"""
    pass

class SystemInfoError(PromptGenerationError):
    """Raised when there's an error processing system information"""
    pass

class MessageFormatError(PromptGenerationError):
    """Raised when message format is invalid"""
    pass

class VendorOperationError(PromptGenerationError):
    """Raised when vendor or operation information is invalid"""
    pass

def _validate_system_info(system_info: Optional[Dict]) -> None:
    """Validate system information structure"""
    if system_info is not None and not isinstance(system_info, dict):
        raise SystemInfoError("System info must be a dictionary or None")

def _validate_message_history(message_history: List[Dict[str, str]]) -> None:
    """Validate message history format"""
    if not isinstance(message_history, list):
        raise MessageFormatError("Message history must be a list")
    
    for msg in message_history:
        if not isinstance(msg, dict):
            raise MessageFormatError("Each message must be a dictionary")
        if 'role' not in msg or 'content' not in msg:
            raise MessageFormatError("Messages must contain 'role' and 'content' keys")
        if msg['role'] not in ['system', 'user', 'assistant']:
            raise MessageFormatError(f"Invalid message role: {msg['role']}")

def _validate_vendor_operation(system_info: Dict) -> Tuple[str, str]:
    """Validate and extract vendor and operation information"""
    user_select = system_info.get('user_select_info', {})
    vendor = user_select.get('selected_vendor', '')
    operation = user_select.get('selected_operation', '')
    
    if not vendor:
        raise VendorOperationError("No vendor selected")
    if not operation:
        raise VendorOperationError("No operation selected")
    
    return vendor.capitalize(), operation.capitalize()

def format_system_info(system_info: Optional[Dict] = None) -> str:
    """Format system information into a readable string"""
    try:
        _validate_system_info(system_info)
        
        if not system_info:
            return "No system information available"

        system_details = []
        
        # Extract OS info
        if os_info := system_info.get('os_info', {}):
            try:
                system = os_info.get('system', 'Unknown')
                version = os_info.get('version', 'Unknown')
                distro = os_info.get('distro', 'Unknown')
                system_details.append(f"OS Info: {system} (Version: {version})")
                if distro != 'Unknown':
                    system_details.append(f"OS Distribution Info: {distro}")
            except Exception as e:
                raise PromptGenerationError(f"Error formatting OS info: {str(e)}")

        # Extract Terminal info
        if terminal_info := system_info.get('terminal_info', {}):
            try:
                term_type = terminal_info.get('terminal_type', 'Unknown')
                term_program = terminal_info.get('terminal_program', 'Unknown')
                term_version = terminal_info.get('terminal_version', 'Unknown')
                system_details.append(f"Terminal Info: {term_type} (Program: {term_program}, Version: {term_version})")
            except Exception as e:
                raise PromptGenerationError(f"Error formatting terminal info: {str(e)}")

        # Extract Kubernetes info
        if k8s_info := system_info.get('kubernetes_info', {}):
            try:
                k8s_status = 'Available' if k8s_info.get('kubectl_available') else 'Not Available'
                k8s_version = k8s_info.get('kubectl_version', 'N/A')
                helm_status = 'Available' if k8s_info.get('helm_available') else 'Not Available'
                helm_version = k8s_info.get('helm_version', 'N/A')
                system_details.append(f"Kubernetes Info: {k8s_status} (Version: {k8s_version})")
                system_details.append(f"Helm Info: {helm_status} (Version: {helm_version})")
            except Exception as e:
                raise PromptGenerationError(f"Error formatting Kubernetes info: {str(e)}")

        # Extract Running Services info
        if running_services := system_info.get('running_services_info', []):
            try:
                if running_services:
                    system_details.append("\nDetected Services Info:")
                    for service in running_services:
                        name = service.get('name', 'Unknown')
                        pid = service.get('pid', 'N/A')
                        system_details.append(f"- {name} (PID: {pid})")
            except Exception as e:
                raise PromptGenerationError(f"Error formatting running services info: {str(e)}")

        return '\n'.join(system_details)
    except Exception as e:
        raise PromptGenerationError(f"Error processing system information: {str(e)}")

def format_prompt(message_history: List[Dict[str, str]], system_info: Optional[Dict] = None) -> List[Dict[str, str]]:
    """Format the message history with a prompt template"""
    try:
        # Validate inputs
        _validate_message_history(message_history)
        _validate_system_info(system_info)

        # Get formatted system information
        try:
            system_context = format_system_info(system_info)
        except SystemInfoError as e:
            raise PromptGenerationError(f"Error formatting system info: {str(e)}")
        
        # Get vendor and operation information
        try:
            if system_info:
                vendor, operation = _validate_vendor_operation(system_info)
            else:
                vendor, operation = "Unknown", "Unknown"
        except VendorOperationError as e:
            raise PromptGenerationError(f"Error with vendor/operation: {str(e)}")

        # Get the base prompt template
        base_prompt = get_base_prompt(vendor, operation, system_context)

        try:
            formatted_messages = [base_prompt] + [
                msg for msg in message_history 
                if msg["role"] in ["user", "assistant"]
            ]
        except Exception as e:
            raise PromptGenerationError(f"Error formatting messages: {str(e)}")

        return formatted_messages

    except (SystemInfoError, MessageFormatError, VendorOperationError) as e:
        raise PromptGenerationError(str(e))
    except Exception as e:
        raise PromptGenerationError(f"Unexpected error in prompt generation: {str(e)}")
