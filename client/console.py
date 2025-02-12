# Import standard library for command line argument parsing
import argparse
import json
# Import prompt_toolkit for enhanced command line interface
from prompt_toolkit import PromptSession
from client.sysdetect import SystemTelemetryDetection, SystemDetectionError
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
        
        # Add both vendor and operation to system info
        self.system_info['mode_type'] = mode_type
        self.system_info['selected_vendor'] = selection
        self.system_info['selected_operation'] = obs_operation
        
        # Automatically trigger the installation steps
        try:
            self.message_broker.add_message("")  # Empty message to trigger the prompt
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
                    prompt = f"{obs_operation}_{selection}_agent> "
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
                    self.console.print(json.dumps(self.system_info, indent=2))
                else:
                    try:
                        print("***DEBUG add_message(cmd)", cmd)
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

    def show_streaming_output(self, generator):
        """Show streaming output with live updates"""
        try:
            accumulated_text = ""
            with Live(refresh_per_second=4) as live:
                for content in generator:
                    accumulated_text += content
                    live.update(Text(accumulated_text))
        except Exception as e:
            self.show_error(f"Output error: {str(e)}")


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
            if selection in ['appdynamics', 'datadog', 'dynatrace', 'grafana', 'splunk']:
                mode_type, obs_operation = io.handle_vendor_selection(selection)
                if not obs_operation:
                    return 0
                if obs_operation == "menu":
                    continue
            else:
                mode_type = 'infrastructure'
                obs_operation = None
                # Add infrastructure selection to system info
                io.system_info['mode_type'] = mode_type
                io.system_info['selected_platform'] = selection

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
