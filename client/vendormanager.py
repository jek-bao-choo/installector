from typing import Optional
from rich.console import Console

class VendorManager:
    def __init__(self, console: Console):
        self.console = console
        self.vendors = ["AppDynamics", "Datadog", "Dynatrace", "Grafana", "Splunk", "exit"]

    def select_vendor(self) -> Optional[str]:
        """Show simple vendor selection in terminal"""
        self.console.print("# Select Observability Vendor", style="bold")
        for idx, vendor in enumerate(self.vendors, 1):
            self.console.print(f"{idx}. {vendor}")
        
        while True:
            try:
                choice = self.console.input("\nEnter number (1-6): ")
                if not choice:
                    return None
                
                choice_idx = int(choice)
                if 1 <= choice_idx <= len(self.vendors):
                    selected = self.vendors[choice_idx - 1]
                    if selected == "exit":
                        return None
                    return selected.lower()
                else:
                    self.console.print("Invalid selection. Please enter a number between 1 and 6.", style="red")
            except ValueError:
                self.console.print("Please enter a valid number.", style="red")
