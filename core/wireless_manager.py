"""
KYKSKN - Wireless Interface Manager
"""

import subprocess
import time
import netifaces
from typing import Optional, List, Tuple
from rich.console import Console
from utils.validators import check_interface_exists, is_monitor_mode
from utils.helpers import run_command, kill_process_by_name
from utils.logger import logger

console = Console()


class WirelessManager:
    """Manage wireless interfaces and monitor mode"""
    
    def __init__(self):
        self.original_interface = None
        self.monitor_interface = None
        self.original_mac = None
        
    def get_wireless_interfaces(self) -> List[str]:
        """Get list of wireless interfaces"""
        interfaces = []
        try:
            result = run_command(['iwconfig'], timeout=5)
            if result and result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'IEEE 802.11' in line or 'ESSID' in line:
                        interface = line.split()[0]
                        if interface and not interface.startswith('mon'):
                            interfaces.append(interface)
            
            # Alternative method using netifaces
            if not interfaces:
                for iface in netifaces.interfaces():
                    if iface.startswith('wl') or iface.startswith('wlan'):
                        interfaces.append(iface)
                        
        except Exception as e:
            logger.error(f"Error getting wireless interfaces: {e}")
        
        return interfaces
    
    def get_interface_mac(self, interface: str) -> Optional[str]:
        """Get MAC address of interface"""
        try:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_LINK in addrs:
                return addrs[netifaces.AF_LINK][0]['addr'].upper()
        except Exception as e:
            logger.error(f"Error getting MAC address: {e}")
        return None
    
    def is_interface_up(self, interface: str) -> bool:
        """Check if interface is up"""
        try:
            result = run_command(['ip', 'link', 'show', interface], timeout=5)
            if result and result.returncode == 0:
                return 'state UP' in result.stdout
        except Exception:
            pass
        return False
    
    def bring_interface_up(self, interface: str) -> bool:
        """Bring interface up"""
        try:
            result = run_command(['ip', 'link', 'set', interface, 'up'], timeout=5)
            return result and result.returncode == 0
        except Exception as e:
            logger.error(f"Error bringing interface up: {e}")
            return False
    
    def bring_interface_down(self, interface: str) -> bool:
        """Bring interface down"""
        try:
            result = run_command(['ip', 'link', 'set', interface, 'down'], timeout=5)
            return result and result.returncode == 0
        except Exception as e:
            logger.error(f"Error bringing interface down: {e}")
            return False
    
    def kill_interfering_processes(self):
        """Kill processes that might interfere with monitor mode"""
        processes = [
            'NetworkManager',
            'wpa_supplicant',
            'dhclient',
            'avahi-daemon'
        ]
        
        for proc in processes:
            kill_process_by_name(proc)
        
        time.sleep(1)
    
    def enable_monitor_mode(self, interface: str) -> Optional[str]:
        """Enable monitor mode on interface"""
        try:
            logger.info(f"Enabling monitor mode on {interface}")
            
            # Check if already in monitor mode
            if is_monitor_mode(interface):
                self.monitor_interface = interface
                logger.info(f"{interface} already in monitor mode")
                return interface
            
            # Save original interface
            self.original_interface = interface
            self.original_mac = self.get_interface_mac(interface)
            
            # Kill interfering processes
            console.print("[yellow]⚙️  Interfering processes kapatılıyor...[/yellow]")
            self.kill_interfering_processes()
            
            # Bring interface down
            self.bring_interface_down(interface)
            
            # Use airmon-ng to enable monitor mode
            console.print(f"[yellow]⚙️  {interface} monitor moda geçiriliyor...[/yellow]")
            result = run_command(['airmon-ng', 'start', interface], timeout=10)
            
            if result and result.returncode == 0:
                # Find monitor interface name
                time.sleep(2)
                
                # Try common monitor interface names
                possible_names = [
                    f"{interface}mon",
                    f"{interface}mon0",
                    "mon0",
                    "wlan0mon",
                    "wlan1mon"
                ]
                
                for mon_iface in possible_names:
                    if check_interface_exists(mon_iface) and is_monitor_mode(mon_iface):
                        self.monitor_interface = mon_iface
                        self.bring_interface_up(mon_iface)
                        logger.info(f"Monitor mode enabled: {mon_iface}")
                        console.print(f"[green]✓ Monitor mode aktif: {mon_iface}[/green]")
                        return mon_iface
                
                # If not found, check all interfaces
                for iface in self.get_wireless_interfaces():
                    if is_monitor_mode(iface):
                        self.monitor_interface = iface
                        logger.info(f"Monitor mode enabled: {iface}")
                        console.print(f"[green]✓ Monitor mode aktif: {iface}[/green]")
                        return iface
            
            logger.error("Failed to enable monitor mode")
            return None
            
        except Exception as e:
            logger.error(f"Error enabling monitor mode: {e}")
            console.print(f"[red]✗ Monitor mode hatası: {e}[/red]")
            return None
    
    def disable_monitor_mode(self):
        """Disable monitor mode and restore original interface"""
        try:
            if self.monitor_interface:
                logger.info(f"Disabling monitor mode on {self.monitor_interface}")
                console.print(f"[yellow]⚙️  Monitor mode kapatılıyor...[/yellow]")
                
                # Use airmon-ng to stop monitor mode
                run_command(['airmon-ng', 'stop', self.monitor_interface], timeout=10)
                
                time.sleep(2)
                
                # Restart NetworkManager
                run_command(['systemctl', 'start', 'NetworkManager'], timeout=10)
                
                logger.info("Monitor mode disabled")
                console.print("[green]✓ Normal mode'a dönüldü[/green]")
                
        except Exception as e:
            logger.error(f"Error disabling monitor mode: {e}")
    
    def set_channel(self, interface: str, channel: int) -> bool:
        """Set wireless channel"""
        try:
            result = run_command(['iwconfig', interface, 'channel', str(channel)], timeout=5)
            if result and result.returncode == 0:
                logger.info(f"Set channel {channel} on {interface}")
                return True
            
            # Alternative method using iw
            result = run_command(['iw', 'dev', interface, 'set', 'channel', str(channel)], timeout=5)
            if result and result.returncode == 0:
                logger.info(f"Set channel {channel} on {interface}")
                return True
                
        except Exception as e:
            logger.error(f"Error setting channel: {e}")
        
        return False
    
    def get_current_channel(self, interface: str) -> Optional[int]:
        """Get current channel of interface"""
        try:
            result = run_command(['iwconfig', interface], timeout=5)
            if result and result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Frequency' in line or 'Channel' in line:
                        # Extract channel number
                        import re
                        match = re.search(r'Channel[:\s]+(\d+)', line)
                        if match:
                            return int(match.group(1))
        except Exception as e:
            logger.error(f"Error getting channel: {e}")
        
        return None
    
    def get_connected_network(self) -> Optional[Tuple[str, str]]:
        """Get currently connected network SSID and BSSID"""
        try:
            # Try using iwconfig
            result = run_command(['iwconfig'], timeout=5)
            if result and result.returncode == 0:
                ssid = None
                for line in result.stdout.split('\n'):
                    if 'ESSID:' in line:
                        import re
                        match = re.search(r'ESSID:"([^"]+)"', line)
                        if match:
                            ssid = match.group(1)
                            if ssid and ssid != 'off/any':
                                # Get BSSID using iw
                                result2 = run_command(['iw', 'dev'], timeout=5)
                                if result2 and result2.returncode == 0:
                                    for line2 in result2.stdout.split('\n'):
                                        if 'ssid' in line2.lower() and ssid in line2:
                                            # Look for associated AP
                                            pass
                                return (ssid, None)
        except Exception as e:
            logger.error(f"Error getting connected network: {e}")
        
        return None

