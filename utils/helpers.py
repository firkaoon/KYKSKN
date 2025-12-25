"""
KYKSKN - Helper Functions
"""

import subprocess
import time
import signal
import sys
from typing import Optional, List
from rich.console import Console

console = Console()


def run_command(cmd: List[str], timeout: int = 30, capture: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Run a shell command safely"""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        else:
            result = subprocess.run(
                cmd,
                timeout=timeout
            )
        return result
    except subprocess.TimeoutExpired:
        console.print(f"[red]Command timed out: {' '.join(cmd)}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]Command failed: {e}[/red]")
        return None


def kill_process_by_name(process_name: str):
    """Kill all processes with given name"""
    try:
        subprocess.run(
            ['pkill', '-9', process_name],
            capture_output=True,
            timeout=5
        )
    except Exception:
        pass


def cleanup_temp_files(pattern: str):
    """Clean up temporary files"""
    try:
        subprocess.run(
            ['rm', '-f', pattern],
            capture_output=True,
            timeout=5
        )
    except Exception:
        pass


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    console.print("\n\n[yellow]⚠️  Saldırı durduruluyor...[/yellow]")
    cleanup_temp_files("/tmp/kykskn*")
    kill_process_by_name("airodump-ng")
    kill_process_by_name("aireplay-ng")
    console.print("[green]✓ Temizlik tamamlandı. Güle güle![/green]")
    sys.exit(0)


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def format_mac(mac: str) -> str:
    """Format MAC address to standard format"""
    mac = mac.replace('-', ':').replace('.', ':').upper()
    return mac


def format_signal_strength(dbm: int) -> str:
    """Format signal strength with visual indicator"""
    if dbm >= -50:
        bars = "████████"
        color = "green"
    elif dbm >= -60:
        bars = "██████░░"
        color = "green"
    elif dbm >= -70:
        bars = "████░░░░"
        color = "yellow"
    elif dbm >= -80:
        bars = "██░░░░░░"
        color = "yellow"
    else:
        bars = "░░░░░░░░"
        color = "red"
    
    return f"[{color}]{bars}[/{color}] {dbm} dBm"


def get_timestamp() -> str:
    """Get formatted timestamp"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def clear_screen():
    """Clear terminal screen"""
    console.clear()


def press_any_key():
    """Wait for user to press any key"""
    console.print("\n[dim]Devam etmek için Enter'a basın...[/dim]")
    input()

