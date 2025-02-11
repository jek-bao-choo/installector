from typing import Optional
from rich.console import Console

class VendorManager:
    def __init__(self, console: Console):
        self.console = console
        # Define options in categories
        self.categories = {
            "# Instrument an Observability Vendor:": [
                "AppDynamics",
                "Datadog",
                "Dynatrace",
                "Grafana",
                "Splunk"
            ],
            "# Or troubleshoot an Infrastructure Platform:": [
                "Amazon EKS",
                "Azure AKS", 
                "Google GKE",
                "Red Hat OpenShift"
            ],
            "# Misc": [
                "exit"
            ]
        }
        # Create flat list for selection handling
        self.all_options = []
        for category_options in self.categories.values():
            self.all_options.extend(category_options)

    def select_option(self) -> Optional[str]:
        """Show all options in categorized format"""
        current_index = 1
        
        # Print categories and their options
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
                    return selected.lower().replace(" ", "_")
                else:
                    self.console.print(f"Invalid selection. Please enter a number between 1 and {len(self.all_options)}.", style="red")
            except ValueError:
                self.console.print("Please enter a valid number.", style="red")
