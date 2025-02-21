#!/usr/bin/env python3

import platform
import os
import subprocess
import psutil  # For process and service information
import distro  # For detailed Linux distribution info
import logging
from pathlib import Path
import json
from functools import wraps
import signal
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Dict, List, Optional
from rich.console import Console
import shutil
import sys

class SystemDetectionError(Exception):
    """Base exception for system detection errors"""
    pass

class PermissionDeniedError(SystemDetectionError):
    """Raised when permissions are insufficient"""
    pass

class TimeoutError(SystemDetectionError):
    """Raised when an operation takes too long"""
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def with_timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set the timeout handler
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable the alarm
                signal.alarm(0)
            return result
        return wrapper
    return decorator


class SystemTelemetryDetection:
    def __init__(self):
        self.system_info = {}
        self.logger = self._setup_logging()
        self.timeout_seconds = 30  # Default timeout for operations

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("SystemTelemetryCollector")
        logger.setLevel(logging.INFO)
        # Add stream handler for console output instead of file
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(sh)
        return logger

    def get_os_info(self) -> Dict:
        """Collect OS distribution and version information."""
        try:
            os_info = {
                "system": platform.system(),
                "machine": platform.machine(),
                "platform": platform.platform(),
            }

            if platform.system() == "Linux":
                try:
                    os_info.update({
                        "distro": distro.name(True),
                        "version": distro.version(True),
                        "codename": distro.codename()
                    })
                except PermissionError as e:
                    self.logger.error(f"Permission denied accessing Linux distribution info: {e}")
                    raise PermissionDeniedError("Cannot access Linux distribution information")
            elif platform.system() == "Darwin":
                os_info["version"] = platform.mac_ver()[0]
            elif platform.system() == "Windows":
                os_info["version"] = platform.win32_ver()[0]

            return os_info
        except Exception as e:
            self.logger.error(f"Error getting OS info: {e}")
            raise SystemDetectionError(f"Failed to get OS information: {str(e)}")

    def check_kubernetes(self) -> Dict:
        """Check for Kubernetes/kubectl and get version information."""
        k8s_info = {
            "kubectl_available": False,
            "kubectl_version": None,
            "helm_available": False,
            "helm_version": None
        }

        try:
            kubectl_version = subprocess.check_output(["kubectl", "version", "--client", "-o", "json"])
            k8s_info["kubectl_available"] = True
            k8s_info["kubectl_version"] = json.loads(kubectl_version)

            # Check for helm if kubectl is available
            try:
                helm_version = subprocess.check_output(["helm", "version", "--short"]).decode().strip()
                k8s_info["helm_available"] = True
                k8s_info["helm_version"] = helm_version
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.info("Helm not found")

        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.info("kubectl not found")

        return k8s_info

    def get_running_services(self) -> List[Dict]:
        """Get information about running services that can be instrumented."""
        instrumentation_services = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                process_info = proc.info
                # Check for common instrumentation services
                if self._is_instrumentation_service(process_info):
                    service_info = {
                        "name": process_info['name'],
                        "pid": process_info['pid'],
                        "cmdline": process_info['cmdline']
                    }
                    instrumentation_services.append(service_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return instrumentation_services

    def _is_instrumentation_service(self, process_info: Dict) -> bool:
        """Check if a service can be instrumented with OpenTelemetry."""
        instrumentation_service_patterns = [
            'java', 'python', 'node', 'nginx', 'apache',
            'mysql', 'postgresql', 'mongodb', 'redis',
            'elasticsearch', 'kafka', 'rabbitmq'
        ]

        return any(pattern in str(process_info['name']).lower()
                   for pattern in instrumentation_service_patterns)

    def get_log_locations(self) -> Dict[str, str]:
        """Identify common log locations based on OS."""
        log_locations = {}

        if platform.system() == "Linux":
            common_paths = [
                "/var/log",
                "/var/log/syslog",
                "/var/log/messages",
                "/var/log/apache2",
                "/var/log/nginx"
            ]
        elif platform.system() == "Darwin":
            common_paths = [
                "/var/log",
                "/Library/Logs",
                f"/Users/{os.getenv('USER')}/Library/Logs"
            ]
        elif platform.system() == "Windows":
            common_paths = [
                r"C:\Windows\Logs",
                r"C:\ProgramData\logs"
            ]

        for path in common_paths:
            if os.path.exists(path):
                log_locations[path] = self._get_log_files(path)

        return log_locations

    def _get_log_files(self, path: str) -> List[str]:
        """Get list of log files in a directory."""
        log_files = []
        try:
            for entry in Path(path).rglob("*.log"):
                log_files.append(str(entry))
        except PermissionError:
            self.logger.warning(f"Permission denied accessing {path}")
        return log_files

    def get_terminal_info(self) -> Dict[str, Optional[str]]:
        """Collect information about the terminal environment."""
        terminal_info = {
            "terminal_type": None,
            "terminal_size": None,
            "terminal_encoding": None,
            "is_interactive": None,
            "color_support": None,
            "terminal_program": None,
            "shell": None
        }

        try:
            # Get terminal type
            terminal_info["terminal_type"] = os.environ.get("TERM")
            
            # Get terminal size
            try:
                columns, lines = shutil.get_terminal_size()
                terminal_info["terminal_size"] = f"{columns}x{lines}"
            except (AttributeError, ValueError):
                pass

            # Get terminal encoding
            terminal_info["terminal_encoding"] = sys.stdout.encoding

            # Check if running in interactive mode
            terminal_info["is_interactive"] = sys.stdin.isatty()

            # Detect color support
            terminal_info["color_support"] = sys.stdout.isatty()

            # Get terminal program
            terminal_info["terminal_program"] = os.environ.get("TERM_PROGRAM")

            # Get current shell
            terminal_info["shell"] = os.environ.get("SHELL")

            # Additional environment variables that might be useful
            if os.environ.get("COLORTERM"):
                terminal_info["color_term"] = os.environ.get("COLORTERM")
            
            if os.environ.get("TERM_PROGRAM_VERSION"):
                terminal_info["terminal_version"] = os.environ.get("TERM_PROGRAM_VERSION")

        except Exception as e:
            self.logger.error(f"Error getting terminal information: {e}")
            raise SystemDetectionError(f"Failed to get terminal information: {str(e)}")

        return terminal_info

    def collect_system_info(self, console: Optional['Console'] = None) -> dict:
        """Collect system information during initialization"""
        try:
            if console:
                console.print("Collecting system information...", style="yellow")
            system_info = self.collect_all()
            if console:
                console.print("System information collected successfully.", style="green")
            return system_info
        except SystemDetectionError as e:
            if console:
                console.print(f"Warning: System detection partial failure: {str(e)}", style="yellow")
            return {}
        except Exception as e:
            if console:
                console.print(f"Warning: Could not collect system information: {str(e)}", style="yellow")
            return {}

    def collect_all(self) -> Dict:
        """Collect all system information."""
        try:
            with ThreadPoolExecutor() as executor:
                future_os = executor.submit(self.get_os_info)
                future_terminal = executor.submit(self.get_terminal_info)
                future_k8s = executor.submit(self.check_kubernetes)
                future_services = executor.submit(self.get_running_services)

                try:
                    self.system_info = {
                        "os_info": future_os.result(timeout=self.timeout_seconds),
                        "terminal_info": future_terminal.result(timeout=self.timeout_seconds),
                        "kubernetes_info": future_k8s.result(timeout=self.timeout_seconds),
                        "running_services_info": future_services.result(timeout=self.timeout_seconds)
                    }
                except TimeoutError:
                    self.logger.error("System information collection timed out")
                    raise SystemDetectionError("Operation timed out while collecting system information")

        except Exception as e:
            self.logger.error(f"Error collecting system information: {e}")
            raise SystemDetectionError(f"Failed to collect system information: {str(e)}")

        return self.system_info


def main():
    collector = SystemTelemetryDetection()
    system_info = collector.collect_all()
    print(json.dumps(system_info, indent=2))


if __name__ == "__main__":
    main()
