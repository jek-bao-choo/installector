#!/usr/bin/env python

import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import MarkdownLexer
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live


class SimpleCompleter(Completer):
    """Simple completer that completes from a list of words"""

    def __init__(self, words):
        self.words = words

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for cmd in self.words:
            if cmd.startswith(word):
                yield Completion(cmd, start_position=-len(word))


class SimpleIO:
    def __init__(self,
                 user_color="blue",
                 error_color="red",
                 warning_color="yellow"):
        # Initialize rich console for formatted output
        self.console = Console()

        # Initialize prompt session with history and completion
        self.session = PromptSession(
            lexer=PygmentsLexer(MarkdownLexer),
            completer=SimpleCompleter(['help', 'exit', 'clear', 'show']),
        )

        # Store color settings
        self.user_color = user_color
        self.error_color = error_color
        self.warning_color = warning_color

    def get_input(self, prompt="> "):
        """Get input from user with completion and history"""
        try:
            return self.session.prompt(prompt)
        except KeyboardInterrupt:
            return None
        except EOFError:
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

    def show_streaming_output(self, generator):
        """Show streaming output with live updates"""
        with Live(refresh_per_second=4) as live:
            for content in generator:
                live.update(Text(content))


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple terminal IO demo")
    parser.add_argument('--no-color', action='store_true', help='Disable colors')
    args = parser.parse_args()

    # Initialize IO
    io = SimpleIO()

    # Main interaction loop
    while True:
        cmd = io.get_input("demo> ")

        if not cmd:
            continue

        cmd = cmd.strip()

        if cmd == 'exit':
            break
        elif cmd == 'help':
            io.show_markdown("""
# Available Commands
- `help`: Show this help
- `exit`: Exit the program
- `clear`: Clear the screen
- `show`: Show a demo of different outputs
            """)
        elif cmd == 'clear':
            io.console.clear()
        elif cmd == 'show':
            # Demo different types of output
            io.show_output("This is normal output")
            io.show_error("This is an error message")
            io.show_warning("This is a warning message")

            # Demo streaming output
            def stream_demo():
                for i in range(5):
                    yield f"Streaming line {i + 1}..."

            io.show_streaming_output(stream_demo())

            # Demo markdown
            io.show_markdown("""
# Markdown Demo
This is *italic* and **bold**

- List item 1
- List item 2

```python
def hello():
    print("Hello, world!")
```
            """)
        else:
            io.show_error(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
