from typing import Optional
from rich.console import Console
from rich.markdown import Markdown

class MainMenuError(Exception):
    """Base exception for main menu errors"""
    pass

class MainMenu:
    def __init__(self, console: Console):
        try:
            if not isinstance(console, Console):
                raise MainMenuError("Invalid console object provided")
            
            self.console = console
            # Define options in categories
            self.categories = {
                "# Manage an Observability Vendor agent:": [
                    "AppDynamics Server Agent",
                    "DataDog Agent",
                    "Dynatrace OneAgent",
                    "Grafana Agent",
                    "Splunk OpenTelemetry Collector"
                ],
                "# Or manage an Infrastructure Vendor platform:": [
                    "Amazon EKS",
                    "Azure AKS", 
                    "Google GKE",
                    "Red Hat OpenShift"
                ],
                "# Misc": [
                    "help",
                    "exit"
                ]
            }
            # Create flat list for selection handling
            try:
                self.all_options = []
                for category_options in self.categories.values():
                    self.all_options.extend(category_options)
                if not self.all_options:
                    raise MainMenuError("No menu options available")
            except Exception as e:
                raise MainMenuError(f"Failed to initialize menu options: {str(e)}")
        except MainMenuError as e:
            raise e
        except Exception as e:
            raise MainMenuError(f"Failed to initialize MainMenu: {str(e)}")

    def show_help(self) -> None:
        """Show help information for the main menu"""
        try:
            self.console.print(Markdown("""
# Available Options and Commands

## Observability Vendor Options:
- `AppDynamics Server Agent`: Manage AppDynamics Server Agent operations
- `DataDog Agent`: Manage DataDog Agent operations
- `Dynatrace OneAgent`: Manage Dynatrace OneAgent operations
- `Grafana Agent`: Manage Grafana Agent operations
- `Splunk OpenTelemetry Collector`: Manage Splunk OpenTelemetry Collector operations

## Infrastructure Platform Options:
- `Amazon EKS`: Manage Amazon Elastic Kubernetes Service
- `Azure AKS`: Manage Azure Kubernetes Service
- `Google GKE`: Manage Google Kubernetes Engine
- `Red Hat OpenShift`: Manage OpenShift Container Platform

## Available Commands:
- `help`: Show this help menu
- `exit`: Exit the program
- `system`: Show detected system information
- `clear`: Clear the screen

## Usage Tips:
1. Select a vendor to manage agent operations
2. Select a platform to manage infrastructure
3. Use number keys (1-{len(self.all_options)}) to make your selection
4. Type 'help' anytime to see this information again
            """))
        except Exception as e:
            self.console.print(f"Error displaying help: {str(e)}", style="red")

    def _validate_choice(self, choice: str) -> int:
        """Validate and convert user input to menu index"""
        try:
            if not choice.strip():
                raise MainMenuError("Empty selection")
            
            choice_idx = int(choice)
            if not 1 <= choice_idx <= len(self.all_options):
                raise MainMenuError(f"Selection must be between 1 and {len(self.all_options)}")
            
            return choice_idx
        except ValueError:
            raise MainMenuError("Please enter a valid number")
        except Exception as e:
            raise MainMenuError(f"Invalid selection: {str(e)}")

    def _print_menu(self) -> None:
        """Print the menu options"""
        try:
            current_index = 1
            for category, options in self.categories.items():
                self.console.print(f"\n{category}", style="bold")
                for option in options:
                    self.console.print(f"{current_index}. {option}")
                    current_index += 1
        except Exception as e:
            raise MainMenuError(f"Error displaying menu: {str(e)}")

    def select_option(self) -> Optional[str]:
        """Show main menu and handle selection"""
        try:
            self._print_menu()
            
            while True:
                try:
                    choice = self.console.input(f"\nEnter number (1-{len(self.all_options)}): ")
                    
                    try:
                        choice_idx = self._validate_choice(choice)
                    except MainMenuError as e:
                        self.console.print(str(e), style="red")
                        continue
                    
                    selected = self.all_options[choice_idx - 1]
                    
                    # Handle special options
                    if selected == "exit":
                        return None
                    elif selected == "help":
                        self.show_help()
                        # After showing help, show the menu again
                        return self.select_option()
                    
                    # Return normal selection
                    return selected.lower().replace(" ", "_")
                    
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
