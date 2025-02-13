import subprocess
from rich.console import Console
from rich.markdown import Markdown
from typing import Optional

class VerificationOutput:
    def __init__(self, console: Console):
        self.console = console

    def run_verification(self, verify_command: Optional[str]) -> bool:
        """Run verification command and display results
        Returns True if verification succeeded, False otherwise"""
        if not verify_command:
            return True
            
        try:
            self.console.print(Markdown("\n## Running verification command:"))
            self.console.print(Markdown(f"```bash\n{verify_command}\n```"))
            
            # Execute the verification command and capture output
            result = subprocess.run(
                verify_command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            # Show the command output
            self.console.print(Markdown("\n## Verification Results:"))
            if result.stdout:
                self.console.print(Markdown("### Output:"))
                self.console.print(Markdown(f"```\n{result.stdout}\n```"))
            if result.stderr:
                self.console.print(Markdown("### Errors:"))
                self.console.print(Markdown(f"```\n{result.stderr}\n```"))
            
            # Show the return code
            status = "✅ Success" if result.returncode == 0 else "❌ Failed"
            self.console.print(Markdown(f"\n**Status**: {status} (return code: {result.returncode})"))
            
            return result.returncode == 0
            
        except Exception as e:
            self.console.print(f"\nError running verification command: {str(e)}", style="red")
            return False
