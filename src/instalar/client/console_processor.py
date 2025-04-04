import json
from typing import Optional, Tuple
from rich.markdown import Markdown

class CommandProcessor:
    """Processes user commands and handles command loop logic"""
    
    def __init__(self, terminal):
        self.terminal = terminal
    
    def handle_vendor_selection(self, selection: str) -> Tuple[str, Optional[str]]:
        """Handle vendor selection and operations menu"""
        mode_type = 'observability'
        # Show observability operations menu for vendors
        obs_menu = self.terminal.obs_menu(self.terminal.console, selection)
        obs_operation = obs_menu.select_option()
        if not obs_operation:
            return mode_type, None
        if obs_operation == "menu":
            return mode_type, "menu"
        
        # Initialize user_select_info if it doesn't exist
        if 'user_select_info' not in self.terminal.system_info:
            self.terminal.system_info['user_select_info'] = {}
            
        # Add both vendor and operation to system info under user_select_info
        self.terminal.system_info['user_select_info']['mode_type'] = mode_type
        self.terminal.system_info['user_select_info']['selected_vendor'] = selection
        self.terminal.system_info['user_select_info']['selected_operation'] = obs_operation
        
        # Construct a meaningful message based on selections
        try:
            message = f"Please provide instructions for {obs_operation} operation of {selection}"
            self.terminal.message_broker.add_message(message)
            self.terminal.show_streaming_output(self.terminal.message_broker.get_response())
        except Exception as e:
            self.terminal.show_error(f"Error processing command: {str(e)}")
        
        return mode_type, obs_operation

    def handle_command_loop(self, mode_type: str, selection: str, obs_operation: Optional[str] = None) -> bool:
        """Handle the command prompt loop. Returns True if should return to main menu"""
        while True:
            try:
                # Update prompt to show operation for observability mode
                if mode_type == 'observability':
                    prompt = f"{obs_operation}_{selection}> "
                else:
                    prompt = f"{selection}> "
                    
                cmd = self.terminal.get_input(prompt)

                if not cmd:
                    continue

                cmd = cmd.strip()

                if cmd in ('exit', 'close', 'end'):
                    return False  # Exit program
                elif cmd in ('home', 'main', 'menu'):
                    return True  # Return to main menu
                elif cmd == 'help':
                    self.terminal.show_markdown("""
                    # Available Commands
                    - `help`: Show this help
                    - `exit`: Exit/close/end the program
                    - `close`: Exit/close/end the program
                    - `end`: Exit/close/end the program
                    - `clear`: Clear the screen
                    - `system`: Show detected system information
                    - `menu`: Return to main menu
                    - `main`: Return to main menu
                    - `home`: Return to main menu
                    """)
                elif cmd == 'clear':
                    self.terminal.console.clear()
                elif cmd == 'system':
                    self.terminal.show_markdown("# System Information")
                    # Initialize exec_verify_info if it doesn't exist
                    if 'exec_verify_info' not in self.terminal.system_info:
                        self.terminal.system_info['exec_verify_info'] = {}
                    # Add current commands to system info under exec_verify_info
                    if self.terminal.last_exec_command:
                        self.terminal.system_info['exec_verify_info']['last_exec_command'] = self.terminal.last_exec_command
                    if self.terminal.last_verify_command:
                        self.terminal.system_info['exec_verify_info']['last_verify_command'] = self.terminal.last_verify_command
                    self.terminal.console.print(json.dumps(self.terminal.system_info, indent=2))
                else:
                    try:
                        self.terminal.message_broker.add_message(cmd)
                        self.terminal.show_streaming_output(self.terminal.message_broker.get_response())
                    except Exception as e:
                        self.terminal.show_error(f"Error processing command: {str(e)}")

            except Exception as e:
                self.terminal.show_error(f"Command processing error: {str(e)}")
                continue
                
    def get_command_confirmation(self) -> bool:
        """Ask user to confirm if they executed the command
        Returns True if user confirmed execution, False otherwise"""
        from rich.text import Text
        
        while True:
            # Use cyan color for the prompt text, similar to Aider
            prompt_text = Text()
            prompt_text.append("Executed the command?  ", style="cyan")
            prompt_text.append("(Y)es/(N)o  ", style="cyan dim")
            prompt_text.append("[Yes]", style="cyan bold")
            prompt_text.append(": ", style="cyan")
            
            self.terminal.console.print(prompt_text, end="")
            response = self.terminal.get_input("")  # Empty prompt since we already printed it
            
            # Handle empty input (just Enter) as Yes
            if not response or response.strip() == "":
                response = "yes"
            if response and response.lower() in ['yes', 'y', 'no', 'n']:
                break
            self.terminal.show_warning("Please answer Yes or No")
        
        if response.lower().startswith('n'):
            self.terminal.show_warning("Please execute the command before proceeding to the next step")
            return False
            
        # If user confirmed execution, run verification
        verifier = self.terminal.verification_class(self.terminal.console)
        success, result = verifier.run_verification(self.terminal.last_verify_command)
        
        # Store verification info
        if 'exec_verify_info' not in self.terminal.system_info:
            self.terminal.system_info['exec_verify_info'] = {}
        self.terminal.system_info['exec_verify_info']['last_verification_result'] = result
        self.terminal.system_info['exec_verify_info']['last_verification_status'] = success

        # Handle the verification status
        try:
            verifier.handle_verification_status(
                success, 
                result,
                self.terminal.message_broker,
                self.terminal.last_exec_command,
                self.terminal.last_verify_command
            )
            self.terminal.show_streaming_output(self.terminal.message_broker.get_response())
        except Exception as e:
            self.terminal.show_error(f"Error handling verification status: {str(e)}")
        
        return success
