# Import standard library for command line argument parsing
import argparse
import json
# Import prompt_toolkit for enhanced command line interface
from prompt_toolkit import PromptSession
from client.sysdetect import SystemTelemetryDetection, SystemDetectionError
from client.verify_execution import VerificationOutput
from typing import Optional, Tuple
from client.main_menu import MainMenu
from client.obs_menu import ObsMenu
# Import completion utilities for command auto-completion
from prompt_toolkit.completion import Completer, Completion
from server.message_broker import MessageBroker, MessageBrokerError
# Import syntax highlighting utilities
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import MarkdownLexer
# Import rich library components for terminal formatting
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live


# Define custom autocomplete class
class AutoCompleter(Completer):
    """Simple completer that completes from a list of words"""
    def __init__(self, words):
        # Store list of available commands for completion
        self.words = words

    def get_completions(self, document, complete_event):
        # Get the partial word the user is typing
        word = document.get_word_before_cursor()
        # Check each command if it matches the partial word
        for cmd in self.words:
            if cmd.startswith(word):
                # Yield matching commands as completion options
                yield Completion(cmd, start_position=-len(word))


# Define main terminal interface class
class SimpleTerminal:
    def __init__(self, user_color="blue", error_color="red", warning_color="yellow"):
        # Initialize rich console for formatted output
        self.console = Console()
        
        # Track last commands
        self.last_exec_command = None
        self.last_verify_command = None
        
        # Initialize vendor manager
        self.vendor_manager = MainMenu(self.console)

        # Initialize and run system detection FIRST
        detector = SystemTelemetryDetection()
        self.system_info = detector.collect_system_info(self.console)

        # THEN create message broker instance with system info
        self.message_broker = MessageBroker(system_info=self.system_info)
        
        # Set up prompt session with markdown highlighting and command completion
        self.session = PromptSession(
            lexer=PygmentsLexer(MarkdownLexer),
            completer=AutoCompleter(['help', 'exit', 'clear', 'show', 'close', 'end', 'system']),
        )

        # Store color preferences for different message types
        self.user_color = user_color
        self.error_color = error_color
        self.warning_color = warning_color


    def get_input(self, prompt="> ") -> Optional[str]:
        """Get input from user with completion and history"""
        try:
            return self.session.prompt(prompt)
        except KeyboardInterrupt:
            self.show_warning("\nOperation cancelled by user")
            return None
        except EOFError:
            self.show_warning("\nExit signal received")
            return None
        except Exception as e:
            self.show_error(f"Input error: {str(e)}")
            return None

    def show_output(self, message, style=None):
        """Show normal output with optional styling"""
        # Create styled text object
        text = Text(message)
        if style:
            text.stylize(style)
        # Print the text using rich console
        self.console.print(text)

    def show_error(self, message):
        """Show error message in red"""
        # Print error message with error color
        self.console.print(Text(message, style=self.error_color))

    def show_warning(self, message):
        """Show warning message in yellow"""
        # Print warning message with warning color
        self.console.print(Text(message, style=self.warning_color))

    def handle_vendor_selection(self, selection: str) -> Tuple[str, Optional[str]]:
        """Handle vendor selection and operations menu"""
        mode_type = 'observability'
        # Show observability operations menu for vendors
        obs_menu = ObsMenu(self.console, selection)
        obs_operation = obs_menu.select_option()
        if not obs_operation:
            return mode_type, None
        if obs_operation == "menu":
            return mode_type, "menu"
        
        # Initialize user_select_info if it doesn't exist
        if 'user_select_info' not in self.system_info:
            self.system_info['user_select_info'] = {}
            
        # Add both vendor and operation to system info under user_select_info
        self.system_info['user_select_info']['mode_type'] = mode_type
        self.system_info['user_select_info']['selected_vendor'] = selection
        self.system_info['user_select_info']['selected_operation'] = obs_operation
        
        # Construct a meaningful message based on selections
        try:
            message = f"Please provide instructions for {obs_operation} operation of {selection}"
            self.message_broker.add_message(message)
            self.show_streaming_output(self.message_broker.get_response())
        except MessageBrokerError as e:
            self.show_error(f"Message broker error: {str(e)}")
        except Exception as e:
            self.show_error(f"Error processing command: {str(e)}")
        
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
                    
                cmd = self.get_input(prompt)

                if not cmd:
                    continue

                cmd = cmd.strip()

                if cmd in ('exit', 'close', 'end'):
                    return False  # Exit program
                elif cmd in ('home', 'main', 'menu'):
                    return True  # Return to main menu
                elif cmd == 'help':
                    self.show_markdown("""
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
                    self.console.clear()
                elif cmd == 'system':
                    self.show_markdown("# System Information")
                    # Initialize exec_verify_info if it doesn't exist
                    if 'exec_verify_info' not in self.system_info:
                        self.system_info['exec_verify_info'] = {}
                    # Add current commands to system info under exec_verify_info
                    if self.last_exec_command:
                        self.system_info['exec_verify_info']['last_exec_command'] = self.last_exec_command
                    if self.last_verify_command:
                        self.system_info['exec_verify_info']['last_verify_command'] = self.last_verify_command
                    self.console.print(json.dumps(self.system_info, indent=2))
                else:
                    try:
                        # print("***DEBUG add_message(cmd)", cmd)
                        self.message_broker.add_message(cmd)
                        self.show_streaming_output(self.message_broker.get_response())
                    except MessageBrokerError as e:
                        self.show_error(f"Message broker error: {str(e)}")
                    except Exception as e:
                        self.show_error(f"Error processing command: {str(e)}")

            except Exception as e:
                self.show_error(f"Command processing error: {str(e)}")
                continue

    def show_markdown(self, markdown_text):
        """Show formatted markdown content"""
        # Convert markdown to rich format and print
        md = Markdown(markdown_text)
        self.console.print(md)

    def _extract_command_from_tags(self, cmd_block: str) -> Optional[str]:
        """Extract command from between <code> tags"""
        if '<code>' in cmd_block and '</code>' in cmd_block:
            return cmd_block.split('<code>')[1].split('</code>')[0].strip()
        return None

    def _format_command_block(self, cmd: str, block_type: str) -> Text:
        """Format a command block with proper styling
        block_type should be either 'exec' or 'verify'"""
        result = Text()
        result.append('\n')
        # Add a separator line before command
        result.append('─' * 80 + '\n', style="dim")
        # Add command section header
        header = 'Execute Command:' if block_type == 'exec' else 'Verify Command:'
        result.append(header, style="bold cyan")
        result.append('\n\n')
        # Add command with syntax highlighting
        result.append(cmd, style="bold white on black")
        result.append('\n')
        # Add a separator line after command
        result.append('─' * 80 + '\n', style="dim")
        return result

    def _format_exec_blocks(self, text: str) -> Text:
        """Format execution code blocks and store execution command"""
        result = Text()
        print("\n***DEBUG _format_exec_blocks input:", text)
        
        # Try execution_code tags
        parts = text.split('<execution_code>')
        if len(parts) > 1:  # Found execution_code tags
            for i, part in enumerate(parts):
                if i == 0:
                    result.append(part)
                else:
                    exec_parts = part.split('</execution_code>', 1)
                    if len(exec_parts) >= 1:
                        cmd = exec_parts[0].strip()
                        if cmd:
                            result.append(self._format_command_block(cmd, 'exec'))
                            self.last_exec_command = cmd
                            print("***DEBUG Captured exec command:", self.last_exec_command)
                        
                        if len(exec_parts) > 1:
                            result.append(exec_parts[1])
        else:  # Try backticks as fallback
            parts = text.split('```')
            for i, part in enumerate(parts):
                if i == 0:
                    result.append(part)
                elif i % 2 == 1:  # Inside backticks
                    # Remove language identifier if present
                    cmd_lines = part.strip().split('\n')
                    if cmd_lines:
                        if cmd_lines and cmd_lines[0].lower().strip() in ['bash', 'shell', 'sh']:
                            cmd = '\n'.join(cmd_lines[1:])
                        else:
                            cmd = part.strip()
                        result.append(self._format_command_block(cmd, 'exec'))
                        self.last_exec_command = cmd.strip()
                        print("***DEBUG Captured exec command from backticks:", self.last_exec_command)
                else:  # Outside backticks
                    result.append(part)
        
        return result

    def _format_verify_blocks(self, text: str) -> Text:
        """Format verification code blocks and store verification command"""
        result = Text()
        print("\n***DEBUG _format_verify_blocks input:", text)
        
        # Try verification_code tags
        parts = text.split('<verification_code>')
        if len(parts) > 1:  # Found verification_code tags
            for i, part in enumerate(parts):
                if i == 0:
                    result.append(part)
                else:
                    verify_parts = part.split('</verification_code>', 1)
                    if len(verify_parts) >= 1:
                        cmd = verify_parts[0].strip()
                        if cmd:
                            result.append(self._format_command_block(cmd, 'verify'))
                            self.last_verify_command = cmd
                            print("***DEBUG Captured verify command:", self.last_verify_command)
                        
                        if len(verify_parts) > 1:
                            result.append(verify_parts[1])
        else:  # Try backticks as fallback
            parts = text.split('```')
            for i, part in enumerate(parts):
                if i == 0:
                    result.append(part)
                elif i % 2 == 1:  # Inside backticks
                    # Remove language identifier if present
                    cmd_lines = part.strip().split('\n')
                    if cmd_lines:
                        if cmd_lines and cmd_lines[0].lower().strip() in ['bash', 'shell', 'sh']:
                            cmd = '\n'.join(cmd_lines[1:])
                        else:
                            cmd = part.strip()
                        result.append(self._format_command_block(cmd, 'verify'))
                        self.last_verify_command = cmd.strip()
                        print("***DEBUG Captured verify command from backticks:", self.last_verify_command)
                else:  # Outside backticks
                    result.append(part)
        
        return result

    def _format_code_block(self, text: str) -> Text:
        """Format text to highlight code blocks with XML-style tags"""
        try:
            # First format exec blocks
            # print("\n***DEBUG _format_code_block input:", text)
            result = self._format_exec_blocks(text)
            if not isinstance(result, Text):
                # print("***DEBUG _format_exec_blocks returned non-Text:", type(result))
                result = Text(str(result))
            
            # Then format verify blocks using the formatted exec blocks
            result_str = str(result)
            # print("\n***DEBUG _format_code_block after exec blocks:", result_str)
            
            verify_result = self._format_verify_blocks(result_str)
            if not isinstance(verify_result, Text):
                # print("***DEBUG _format_verify_blocks returned non-Text:", type(verify_result))
                verify_result = Text(str(verify_result))
                
            return verify_result
        except Exception as e:
            print(f"***DEBUG _format_code_block error: {str(e)}")
            # Return original text wrapped in Text object if formatting fails
            return Text(text)


    def _get_command_confirmation(self) -> bool:
        """Ask user to confirm if they executed the command
        Returns True if user confirmed execution, False otherwise"""
        while True:
            # Use cyan color for the prompt text, similar to Aider
            prompt_text = Text()
            prompt_text.append("Executed the command?  ", style="cyan")
            prompt_text.append("(Y)es/(N)o  ", style="cyan dim")
            prompt_text.append("[Yes]", style="cyan bold")
            prompt_text.append(": ", style="cyan")
            
            self.console.print(prompt_text, end="")
            response = self.get_input("")  # Empty prompt since we already printed it
            
            # Handle empty input (just Enter) as Yes
            if not response or response.strip() == "":
                response = "yes"
            if response and response.lower() in ['yes', 'y', 'no', 'n']:
                break
            self.show_warning("Please answer Yes or No")
        
        if response.lower().startswith('n'):
            self.show_warning("Please execute the command before proceeding to the next step")
            return False
            
        # If user confirmed execution, run verification
        verifier = VerificationOutput(self.console)
        success, result = verifier.run_verification(self.last_verify_command)
        
        # Store verification info
        if 'exec_verify_info' not in self.system_info:
            self.system_info['exec_verify_info'] = {}
        self.system_info['exec_verify_info']['last_verification_result'] = result
        self.system_info['exec_verify_info']['last_verification_status'] = success

        # Handle the verification status
        try:
            verifier = VerificationOutput(self.console)
            verifier.handle_verification_status(
                success, 
                result,
                self.message_broker,
                self.last_exec_command,
                self.last_verify_command
            )
            self.show_streaming_output(self.message_broker.get_response())
        except Exception as e:
            self.show_error(f"Error handling verification status: {str(e)}")
        
        return success

    def show_streaming_output(self, generator):
        """Show streaming output with live updates and Aider-style code highlighting"""
        try:
            if not generator:
                self.show_error("No content received from generator")
                return
                
            accumulated_text = ""
            with Live(refresh_per_second=4) as live:
                for content in generator:
                    if not isinstance(content, str):
                        # print(f"***DEBUG Unexpected content type: {type(content)}")
                        content = str(content)
                    
                    accumulated_text += content
                    try:
                        formatted_text = self._format_code_block(accumulated_text)
                        if not isinstance(formatted_text, Text):
                            # print(f"***DEBUG Unexpected formatted_text type: {type(formatted_text)}")
                            formatted_text = Text(str(formatted_text))
                        live.update(formatted_text)
                    except Exception as format_error:
                        print(f"***DEBUG Formatting error: {str(format_error)}")
                        # Fall back to unformatted text if formatting fails
                        live.update(Text(accumulated_text))
            
            # Get command execution confirmation
            if self.last_exec_command or self.last_verify_command:
                self._get_command_confirmation()
                
        except Exception as e:
            self.show_error(f"Output error: {str(e)}")
            print(f"***DEBUG show_streaming_output error: {str(e)}")


def main():
    try:
        parser = argparse.ArgumentParser(description="Simple terminal IO demo")
        parser.add_argument('--no-color', action='store_true', help='Disable colors')
        args = parser.parse_args()

        io = SimpleTerminal()
        
        while True:  # Main loop
            # Show selection menu using vendor manager
            selection = io.vendor_manager.select_option()
            
            # Exit if no selection made
            if not selection:
                return 0
            
            # Determine type based on selection
            if selection in ['appdynamics_server_agent', 'datadog_agent', 'dynatrace_oneagent', 'grafana_agent', 'splunk_opentelemetry_collector' , 'curl']:
                mode_type, obs_operation = io.handle_vendor_selection(selection)
                if not obs_operation:
                    return 0
                if obs_operation == "menu":
                    continue
            else:
                mode_type = 'infrastructure'
                obs_operation = None
                # Initialize user_select_info if it doesn't exist
                if 'user_select_info' not in io.system_info:
                    io.system_info['user_select_info'] = {}
                    
                # Add infrastructure selection to system info under user_select_info
                io.system_info['user_select_info']['mode_type'] = mode_type
                io.system_info['user_select_info']['selected_platform'] = selection

            # Handle command loop
            should_continue = io.handle_command_loop(mode_type, selection, obs_operation)
            if not should_continue:
                return 0

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
