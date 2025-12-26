"""
KYKSKN - Configuration Settings
"""

# Application Info
APP_NAME = "KYKSKN"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Created by Firkaoon"

# Colors
COLOR_PRIMARY = "cyan"
COLOR_SUCCESS = "green"
COLOR_WARNING = "yellow"
COLOR_ERROR = "red"
COLOR_INFO = "blue"
COLOR_HIGHLIGHT = "magenta"

# Deauth Settings
DEAUTH_PACKETS_PER_BURST = 64
DEAUTH_REASON_CODE = 7  # Class 3 frame received from nonassociated STA
DEAUTH_INTERVAL = 0.1  # seconds between packets

# Scanning Settings
SCAN_TIMEOUT = 10  # seconds
CHANNEL_HOP_INTERVAL = 0.5  # seconds
MAX_SCAN_RETRIES = 3

# Threading Settings
MAX_CONCURRENT_ATTACKS = 50
THREAD_POOL_SIZE = 10

# UI Settings
DASHBOARD_REFRESH_RATE = 2  # updates per second
TABLE_MAX_ROWS = 20

# Logging Settings
LOG_DIR = "logs"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Debug Settings
DEBUG_MODE = True  # Set to False to disable debug messages

# File Paths
TEMP_DIR = "/tmp/kykskn"
SCAN_OUTPUT_PREFIX = "kykskn_scan"

# Required Tools
REQUIRED_TOOLS = [
    "airmon-ng",
    "airodump-ng",
    "aireplay-ng",
    "iwconfig",
    "iw"
]

# Wireless Settings
MONITOR_MODE_SUFFIX = "mon"
DEFAULT_CHANNEL = 6

