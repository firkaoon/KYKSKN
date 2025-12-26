"""
KYKSKN - Configuration Settings
"""

# Application Info
APP_NAME = "KYKSKN"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Multi-Target Deauth Attack Framework"

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
SCAN_TIMEOUT = 60  # seconds - Ağ tarama süresi (1 dakika)
DEEP_SCAN_TIMEOUT = 120  # seconds - Cihaz tarama süresi (2 dakika)
CHANNEL_HOP_INTERVAL = 0.5  # seconds
MAX_SCAN_RETRIES = 3

# Attack Modes - Saldırı Modları
ATTACK_MODES = {
    "gentle_10min": {
        "name": "🟢 Nazik Mod - 10 Dakikada Bir Kes",
        "description": "Her 10 dakikada bir 30 saniye kesinti",
        "risk_level": "DÜŞÜK",
        "color": "green",
        "interval": 600,  # 10 dakika
        "duration": 30,   # 30 saniye
        "type": "periodic"
    },
    "gentle_30min": {
        "name": "🟢 Çok Nazik - 30 Dakikada Bir Kes",
        "description": "Her 30 dakikada bir 30 saniye kesinti",
        "risk_level": "ÇOK DÜŞÜK",
        "color": "green",
        "interval": 1800,  # 30 dakika
        "duration": 30,    # 30 saniye
        "type": "periodic"
    },
    "moderate_5min": {
        "name": "🟡 Orta Mod - 5 Dakika Boyunca Kes",
        "description": "5 dakika boyunca sürekli kesinti",
        "risk_level": "ORTA",
        "color": "yellow",
        "interval": 0,
        "duration": 300,  # 5 dakika
        "type": "continuous"
    },
    "random_10min": {
        "name": "🟡 Düzensiz Mod - 10 Dakika Rastgele (ÖNERİLEN)",
        "description": "10 dakika boyunca rastgele aralıklarla kesinti",
        "risk_level": "ORTA",
        "color": "yellow",
        "interval": "random",  # Rastgele
        "duration": 600,  # Toplam 10 dakika
        "type": "random",
        "min_interval": 30,   # En az 30 saniye bekle
        "max_interval": 180,  # En fazla 3 dakika bekle
        "min_attack": 10,     # En az 10 saniye saldır
        "max_attack": 60      # En fazla 60 saniye saldır
    },
    "aggressive_2min": {
        "name": "🟠 Agresif - 2 Dakikada Bir 20 Saniye Kes",
        "description": "Her 2 dakikada bir 20 saniye kesinti",
        "risk_level": "YÜKSEK",
        "color": "bright_yellow",
        "interval": 120,  # 2 dakika
        "duration": 20,   # 20 saniye
        "type": "periodic"
    },
    "infinite": {
        "name": "🔴 Sonsuza Kadar Kes (YÜKSEK RİSK!)",
        "description": "Durdurulana kadar sürekli kesinti",
        "risk_level": "ÇOK YÜKSEK",
        "color": "red",
        "interval": 0,
        "duration": float('inf'),  # Sonsuz
        "type": "infinite"
    }
}

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

