# Import standard library for command line argument parsing
import argparse
from typing import Optional, Generator
# Import prompt_toolkit for enhanced command line interface
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import MarkdownLexer
# Import rich library components for terminal formatting
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live

# Import local modules
from instalar.client.sysdetect import SystemTelemetryDetection
from instalar.client.verify_execution import VerificationOutput
from instalar.client.main_menu import MainMenu
from instalar.client.obs_menu import ObsMenu
from instalar.server.message_broker import MessageBroker
from instalar.client.console_autocomplete import AutoCompleter
from instalar.client.console_formatter import ConsoleFormatter
from instalar.client.console_processor import CommandProcessor
from instalar.client.console_response import ResponseHandler


class SimpleTerminal:
    def __init__(self, user_color="blue", error_color="red", warning_color="yellow"):
        # Initialize rich console for formatted output
        self.console = Console()
        
        # Track last commands
        self.last_exec_command = None
        self.last_verify_command = None
        
        # Initialize vendor manager and other classes
        self.vendor_manager = MainMenu(self.console)
        self.verification_class = VerificationOutput
        self.obs_menu = ObsMenu

        # Initialize and run system detection
        detector = SystemTelemetryDetection()
        self.system_info = detector.collect_system_info(self.console)

        # Create message broker instance with system info
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
        
        # Initialize command processor
        self.cmd_processor = CommandProcessor(self)

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
        text = Text(message)
        if style:
            text.stylize(style)
        self.console.print(text)

    def show_error(self, message):
        """Show error message in red"""
        self.console.print(Text(message, style=self.error_color))

    def show_warning(self, message):
        """Show warning message in yellow"""
        self.console.print(Text(message, style=self.warning_color))
        
    def show_markdown(self, markdown_text):
        """Show formatted markdown content"""
        md = Markdown(markdown_text)
        self.console.print(md)

    def handle_vendor_selection(self, selection: str):
        """Delegate to command processor"""
        return self.cmd_processor.handle_vendor_selection(selection)
        
    def handle_command_loop(self, mode_type: str, selection: str, obs_operation: Optional[str] = None):
        """Delegate to command processor"""
        return self.cmd_processor.handle_command_loop(mode_type, selection, obs_operation)

    def _update_system_info(self, sections: dict) -> None:
        """Update system info with the latest response sections"""
        if 'last_llm_response' not in self.system_info:
            self.system_info['last_llm_response'] = {}
        
        self.system_info['last_llm_response'] = sections
        
        # Update execution and verification commands if present
        if sections['execution']:
            self.last_exec_command = sections['execution']
        if sections['verification']:
            self.last_verify_command = sections['verification']

    def show_streaming_output(self, generator: Generator[str, None, None]):
        """Show streaming output with live updates and XML section parsing"""
        try:
            if not generator:
                self.show_error("No content received from generator")
                return
                
            accumulated_text = ""
            with Live(refresh_per_second=4) as live:
                for content in generator:
                    if not isinstance(content, str):
                        content = str(content)
                    
                    accumulated_text += content
                    
                    try:
                        # Check for termination signal
                        if "<TERMINATE></TERMINATE>" in accumulated_text:
                            self.console.print(Markdown("\n## 🎉 Operation Complete!"))
                            self.console.print(Markdown("All steps have been successfully completed. Returning to menu..."))
                            return
                        
                        # Extract and process sections
                        sections = ResponseHandler.extract_response_sections(accumulated_text)
                        self._update_system_info(sections)
                        formatted_text = ConsoleFormatter.format_response_text(sections)
                        live.update(formatted_text)
                        
                    except Exception as format_error:
                        print(f"***DEBUG Formatting error: {str(format_error)}")
                        live.update(Text(accumulated_text))
            
            # Get command execution confirmation if we have commands
            if self.last_exec_command or self.last_verify_command:
                self.cmd_processor.get_command_confirmation()
                
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
