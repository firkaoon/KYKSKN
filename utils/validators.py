"""
KYKSKN - Validation Utilities
"""

import re
import os
import subprocess
from typing import Optional


def is_valid_mac(mac: str) -> bool:
    """Validate MAC address format"""
    pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    return bool(pattern.match(mac))


def is_root() -> bool:
    """Check if running as root"""
    return os.geteuid() == 0


def check_tool_exists(tool: str) -> bool:
    """Check if a command-line tool exists"""
    try:
        result = subprocess.run(
            ['which', tool],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def check_interface_exists(interface: str) -> bool:
    """Check if network interface exists"""
    try:
        result = subprocess.run(
            ['ip', 'link', 'show', interface],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def is_monitor_mode(interface: str) -> bool:
    """Check if interface is in monitor mode"""
    try:
        result = subprocess.run(
            ['iwconfig', interface],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'Mode:Monitor' in result.stdout
    except Exception:
        return False


def validate_channel(channel: int) -> bool:
    """Validate WiFi channel number"""
    # 2.4GHz: 1-14, 5GHz: 36-165
    valid_2g = list(range(1, 15))
    valid_5g = list(range(36, 166, 4))
    return channel in valid_2g or channel in valid_5g


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem operations"""
    return re.sub(r'[^\w\-_\. ]', '_', filename)

