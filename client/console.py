# Import standard library for command line argument parsing
import argparse
import json
# Import prompt_toolkit for enhanced command line interface
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style
from client.sysdetect import SystemTelemetryDetection, SystemDetectionError
from typing import Optional
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
        
        # Show selection menu using vendor manager
        selection = io.vendor_manager.select_option()
        
        # Exit if no selection made
        if not selection:
            return 0
        
        # Determine type based on selection
        if selection in ['appdynamics', 'datadog', 'dynatrace', 'grafana', 'splunk']:
            mode_type = 'vendor'
            # Show observability operations menu for vendors
            obs_menu = ObsMenu(io.console, selection)
            use_case = obs_menu.select_option()
            if not use_case:
                return 0
            # Add both vendor and operation to system info
            io.system_info['mode_type'] = mode_type
            io.system_info['selected_vendor'] = selection
            io.system_info['selected_use_case'] = use_case
        else:
            mode_type = 'platform'
            io.system_info['mode_type'] = mode_type
            io.system_info['selected_platform'] = selection

        while True:
            try:
                # Update prompt to show operation for vendors
                if mode_type == 'vendor':
                    prompt = f"{use_case}_{selection}_agent> "
                else:
                    prompt = f"{selection}> "
                    
                cmd = io.get_input(prompt)

                if not cmd:
                    continue

                cmd = cmd.strip()

                if cmd in ('exit', 'close', 'end'):
                    break
                elif cmd == 'help':
                    io.show_markdown("""
                    # Available Commands
                    - `help`: Show this help
                    - `exit`: Exit/close/end the program
                    - `close`: Exit/close/end the program
                    - `end`: Exit/close/end the program
                    - `clear`: Clear the screen
                    - `system`: Show detected system information
                    """)
                elif cmd == 'clear':
                    io.console.clear()
                elif cmd == 'system':
                    io.show_markdown("# System Information")
                    io.console.print(json.dumps(io.system_info, indent=2))
                else:
                    try:
                        io.message_broker.add_message(cmd)
                        io.show_streaming_output(io.message_broker.get_response())
                    except MessageBrokerError as e:
                        io.show_error(f"Message broker error: {str(e)}")
                    except Exception as e:
                        io.show_error(f"Error processing command: {str(e)}")

            except Exception as e:
                io.show_error(f"Command processing error: {str(e)}")
                continue

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
