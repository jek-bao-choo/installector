import subprocess
import shlex
from rich.console import Console
from rich.markdown import Markdown
from typing import Optional

class VerificationError(Exception):
    """Base exception for verification errors"""
    pass

class CommandExecutionError(VerificationError):
    """Raised when there's an error executing the command"""
    pass

class CommandTimeoutError(VerificationError):
    """Raised when command execution times out"""
    pass

class CommandNotFoundError(VerificationError):
    """Raised when the command is not found"""
    pass

class VerificationOutput:
    def __init__(self, console: Console):
        self.console = console

    def run_verification(self, verify_command: Optional[str], timeout: int = 30) -> bool:
        """Run verification command and display results
        
        Args:
            verify_command: Command to execute for verification
            timeout: Maximum time in seconds to wait for command completion
            
        Returns:
            bool: True if verification succeeded, False otherwise
            
        Raises:
            CommandExecutionError: If there's an error executing the command
            CommandTimeoutError: If the command execution times out
            CommandNotFoundError: If the command is not found
        """
        if not verify_command:
            return True
            
        try:
            self.console.print(Markdown("\n## Running verification command:"))
            self.console.print(Markdown(f"```bash\n{verify_command}\n```"))
            
            try:
                # Execute the verification command and capture output
                result = subprocess.run(
                    verify_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            except subprocess.TimeoutExpired as e:
                raise CommandTimeoutError(f"Command timed out after {timeout} seconds")
            except subprocess.SubprocessError as e:
                if "command not found" in str(e).lower():
                    raise CommandNotFoundError(f"Command not found: {shlex.split(verify_command)[0]}")
                raise CommandExecutionError(f"Error executing command: {str(e)}")
            
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
            
        except CommandTimeoutError as e:
            self.console.print(Markdown(f"\n❌ **Timeout Error**: {str(e)}"), style="red")
            return False
        except CommandNotFoundError as e:
            self.console.print(Markdown(f"\n❌ **Command Not Found**: {str(e)}"), style="red")
            return False
        except CommandExecutionError as e:
            self.console.print(Markdown(f"\n❌ **Execution Error**: {str(e)}"), style="red")
            return False
        except Exception as e:
            self.console.print(Markdown(f"\n❌ **Unexpected Error**: {str(e)}"), style="red")
            return False
