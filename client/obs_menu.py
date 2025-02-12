from typing import Optional
from rich.console import Console
from rich.markdown import Markdown

class ObsMenuError(Exception):
    """Base exception for observability menu errors"""
    pass

class ObsMenu:
    def __init__(self, console: Console, vendor: str):
        try:
            if not isinstance(console, Console):
                raise ObsMenuError("Invalid console object provided")
            if not vendor or not isinstance(vendor, str):
                raise ObsMenuError("Invalid vendor name provided")
            
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
                    "menu",
                    "exit"
                ]
            }
            # Create flat list for selection handling
            try:
                self.all_options = []
                for category_options in self.categories.values():
                    self.all_options.extend(category_options)
                if not self.all_options:
                    raise ObsMenuError("No menu options available")
            except Exception as e:
                raise ObsMenuError(f"Failed to initialize menu options: {str(e)}")
        except ObsMenuError as e:
            raise e
        except Exception as e:
            raise ObsMenuError(f"Failed to initialize ObsMenu: {str(e)}")

    def show_help(self) -> None:
        """Show help information for the observability operations"""
        try:
            help_text = f"""
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
            """
            self.console.print(Markdown(help_text))
        except Exception as e:
            self.console.print(f"Error displaying help: {str(e)}", style="red")

    def _validate_choice(self, choice: str) -> int:
        """Validate and convert user input to menu index"""
        try:
            if not choice.strip():
                raise ObsMenuError("Empty selection")
            
            choice_idx = int(choice)
            if not 1 <= choice_idx <= len(self.all_options):
                raise ObsMenuError(f"Selection must be between 1 and {len(self.all_options)}")
            
            return choice_idx
        except ValueError:
            raise ObsMenuError("Please enter a valid number")
        except Exception as e:
            raise ObsMenuError(f"Invalid selection: {str(e)}")

    def _print_menu(self) -> None:
        """Print the menu options"""
        try:
            self.console.print(f"\n# {self.vendor.capitalize()} agent use cases:", style="bold")
            
            current_index = 1
            for category, options in self.categories.items():
                self.console.print(f"\n{category}", style="bold")
                for option in options:
                    self.console.print(f"{current_index}. {option}")
                    current_index += 1
        except Exception as e:
            raise ObsMenuError(f"Error displaying menu: {str(e)}")

    def select_option(self) -> Optional[str]:
        """Show observability operations menu and handle selection"""
        try:
            self._print_menu()
            
            while True:
                try:
                    choice = self.console.input(f"\nEnter number (1-{len(self.all_options)}): ")
                    
                    try:
                        choice_idx = self._validate_choice(choice)
                    except ObsMenuError as e:
                        self.console.print(str(e), style="red")
                        continue
                    
                    selected = self.all_options[choice_idx - 1]
                    
                    # Handle special options
                    if selected == "exit":
                        return None
                    elif selected == "menu":
                        return "menu"  # Special return value to trigger main menu
                    
                    # Return normal selection
                    return selected.lower()
                    
                except KeyboardInterrupt:
                    self.console.print("\nOperation cancelled by user", style="yellow")
                    return None
                except EOFError:
                    self.console.print("\nExit signal received", style="yellow")
                    return None
                except Exception as e:
                    self.console.print(f"Error processing selection: {str(e)}", style="red")
                    continue
                    
        except Exception as e:
            self.console.print(f"Fatal error in menu operation: {str(e)}", style="red")
            return None
