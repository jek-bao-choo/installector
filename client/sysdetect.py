#!/usr/bin/env python3

import platform
import os
import subprocess
import psutil  # For process and service information
import distro  # For detailed Linux distribution info
import logging
from pathlib import Path
import json
from typing import Dict, List, Optional


class SystemTelemetryDetection:
    def __init__(self):
        self.system_info = {}
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("SystemTelemetryCollector")
        logger.setLevel(logging.INFO)
        return logger

    def get_os_info(self) -> Dict:
        """Collect OS distribution and version information."""
        os_info = {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        }

        # Get specific distribution info for Linux
        if platform.system() == "Linux":
            os_info.update({
                "distro": distro.name(True),
                "version": distro.version(True),
                "codename": distro.codename()
            })
        elif platform.system() == "Darwin":  # macOS
            os_info["version"] = platform.mac_ver()[0]
        elif platform.system() == "Windows":
            os_info["version"] = platform.win32_ver()[0]

        return os_info

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

    def collect_all(self) -> Dict:
        """Collect all system information."""
        self.system_info = {
            "os_info": self.get_os_info(),
            "kubernetes_info": self.check_kubernetes(),
            "running_services": self.get_running_services(),
            "log_locations": self.get_log_locations()
        }
        return self.system_info


def main():
    collector = SystemTelemetryDetection()
    system_info = collector.collect_all()
    print(json.dumps(system_info, indent=2))


if __name__ == "__main__":
    main()