# Import required libraries
import argparse  # For parsing command line arguments
from prompt_toolkit import PromptSession  # For enhanced command line input
from prompt_toolkit.completion import Completer, Completion  # For command auto-completion
from client.message_broker import MessageBroker  # For handling chat messages
from prompt_toolkit.lexers import PygmentsLexer  # For syntax highlighting
from pygments.lexers import MarkdownLexer  # For markdown syntax highlighting
from rich.console import Console  # For rich text and formatting in terminal
from rich.markdown import Markdown  # For rendering markdown
from rich.text import Text  # For styled text output
from rich.live import Live  # For live-updating output


class AutoCompleter(Completer):
    """Simple completer that completes from a list of words"""

    def __init__(self, words):
        # Store the list of words to use for completion
        self.words = words

    def get_completions(self, document, complete_event):
        # Get the word being typed
        word = document.get_word_before_cursor()
        # Yield completions for commands that match the current word
        for cmd in self.words:
            if cmd.startswith(word):
                yield Completion(cmd, start_position=-len(word))


class SimpleTerminal:
    def __init__(self,
                 user_color="blue",
                 error_color="red",
                 warning_color="yellow"):
        # Initialize rich console for formatted output
        self.console = Console()
        self.message_broker = MessageBroker()

        # Initialize prompt session with history and completion
        self.session = PromptSession(
            lexer=PygmentsLexer(MarkdownLexer),  # Enable markdown syntax highlighting
            completer=AutoCompleter(['help', 'exit', 'clear', 'show', 'close', 'end']),  # Set available commands
        )

        # Store color settings for different message types
        self.user_color = user_color
        self.error_color = error_color
        self.warning_color = warning_color

    def get_input(self, prompt="> "):
        """Get input from user with completion and history"""
        try:
            # Get input with prompt toolkit advanced features
            return self.session.prompt(prompt)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            return None
        except EOFError:
            # Handle Ctrl+D gracefully
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
        accumulated_text = ""
        with Live(refresh_per_second=4) as live:
            for content in generator:
                accumulated_text += content
                live.update(Text(accumulated_text))


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple terminal IO demo")
    parser.add_argument('--no-color', action='store_true', help='Disable colors')
    args = parser.parse_args()

    # Initialize IO handler
    io = SimpleTerminal()

    # Main interaction loop
    while True:
        # Get user input with custom prompt
        cmd = io.get_input("installector> ")

        # Skip if no input (Ctrl+C/D)
        if not cmd:
            continue

        # Remove leading/trailing whitespace
        cmd = cmd.strip()

        # Handle different commands
        if cmd in ('exit', 'close', 'end'):
            break
        elif cmd == 'help':
            # Show help text in markdown format
            io.show_markdown("""
# Available Commands
- `help`: Show this help
- `exit`: Exit/close/end the program
- `close`: Exit/close/end the program
- `end`: Exit/close/end the program
- `clear`: Clear the screen
            """)
        elif cmd == 'clear':
            # Clear the terminal screen
            io.console.clear()
        else:
            # Send message to broker and stream response
            io.message_broker.add_message(cmd)
            io.show_streaming_output(io.message_broker.get_response())


# Standard Python idiom for running main() when script is executed
if __name__ == "__main__":
    main()
