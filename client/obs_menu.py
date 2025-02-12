from typing import Optional
from rich.console import Console
from rich.markdown import Markdown

class ObsMenu:
    def __init__(self, console: Console, vendor: str):
        self.console = console
        self.vendor = vendor
        # Define options in categories
        self.categories = {
            "# Agent Operations:": [
                "Install",
                "Upgrade",
                "Migrate2",
                "Configure", 
                "Troubleshoot",
                "Uninstall"
            ],
            "# Misc:": [
                "exit"
            ]
        }
        # Create flat list for selection handling
        self.all_options = []
        for category_options in self.categories.values():
            self.all_options.extend(category_options)

    def show_help(self):
        """Show help information for the observability operations"""
        self.console.print(Markdown(f"""
# {self.vendor.capitalize()} Operations Help

## Available Options:
- `Install`: Fresh installation of {self.vendor} agent
- `Upgrade`: Upgrade existing {self.vendor} agent to newer version
- `Migrate`: Migrate {self.vendor} agent configuration between environments
- `Configure`: Modify {self.vendor} agent configuration
- `Troubleshoot`: Diagnose and fix {self.vendor} agent issues
- `Uninstall`: Remove {self.vendor} agent and clean up

## Usage:
1. Select the operation you want to perform
2. Follow the prompts for specific guidance
3. Use 'exit' to return to main menu
        """))

    def select_option(self) -> Optional[str]:
        """Show observability operations menu"""
        self.console.print(f"\n# {self.vendor.capitalize()} agent use cases:", style="bold")
        
        # Print categories and their options
        current_index = 1
        for category, options in self.categories.items():
            self.console.print(f"\n{category}", style="bold")
            for option in options:
                self.console.print(f"{current_index}. {option}")
                current_index += 1
        
        while True:
            try:
                choice = self.console.input(f"\nEnter number (1-{len(self.all_options)}): ")
                if not choice:
                    return None
                
                choice_idx = int(choice)
                if 1 <= choice_idx <= len(self.all_options):
                    selected = self.all_options[choice_idx - 1]
                    if selected == "exit":
                        return None
                    return selected.lower()
                else:
                    self.console.print(f"Invalid selection. Please enter a number between 1 and {len(self.all_options)}.", style="red")
            except ValueError:
                self.console.print("Please enter a valid number.", style="red")
