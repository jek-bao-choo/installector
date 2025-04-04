from rich.text import Text
from rich.markdown import Markdown

class ConsoleFormatter:
    """Handles formatting of text and commands for display"""
    
    @staticmethod
    def format_command_block(cmd: str, block_type: str) -> Text:
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

    @staticmethod
    def format_response_text(sections: dict) -> Text:
        """Format the response sections into displayable text"""
        formatted_text = Text()
        
        if sections['title']:
            formatted_text.append(f"\n## {sections['title']}\n\n", style="bold cyan")
        
        if sections['description']:
            formatted_text.append(f"{sections['description']}\n\n")
            
        if sections['execution']:
            formatted_text.append(ConsoleFormatter.format_command_block(sections['execution'], 'exec'))
            
        if sections['expected']:
            formatted_text.append("\nExpected Outcome:\n", style="bold yellow")
            formatted_text.append(f"{sections['expected']}\n")
            
        if sections['verification']:
            formatted_text.append(ConsoleFormatter.format_command_block(sections['verification'], 'verify'))
            
        if sections['conclusion']:
            formatted_text.append(f"\n{sections['conclusion']}\n", style="italic")
            
        return formatted_text
