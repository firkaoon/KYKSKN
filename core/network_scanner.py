"""
KYKSKN - Network Scanner
"""

import subprocess
import time
import csv
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from rich.console import Console
from utils.helpers import run_command, cleanup_temp_files
from utils.logger import logger
from config.settings import SCAN_TIMEOUT, TEMP_DIR

console = Console()


@dataclass
class AccessPoint:
    """Access Point data structure"""
    bssid: str
    essid: str
    channel: int
    encryption: str
    power: int
    beacons: int
    clients: List[str]
    
    def __str__(self):
        return f"{self.essid} ({self.bssid}) - Ch:{self.channel} - {self.power}dBm"


@dataclass
class Client:
    """Client device data structure"""
    mac: str
    bssid: str
    power: int
    packets: int
    
    def __str__(self):
        return f"{self.mac} -> {self.bssid} ({self.power}dBm)"


class NetworkScanner:
    """Scan for wireless networks and clients"""
    
    def __init__(self, interface: str):
        self.interface = interface
        self.access_points: Dict[str, AccessPoint] = {}
        self.clients: Dict[str, Client] = {}
        self.scan_process = None
        
        # Create temp directory
        os.makedirs(TEMP_DIR, exist_ok=True)
    
    def start_scan(self, channel: Optional[int] = None, duration: int = SCAN_TIMEOUT) -> bool:
        """Start airodump-ng scan"""
        try:
            # Clean up old scan files
            cleanup_temp_files(f"{TEMP_DIR}/scan-*")
            
            output_file = f"{TEMP_DIR}/scan"
            
            # Build command
            cmd = [
                'airodump-ng',
                '--output-format', 'csv',
                '-w', output_file,
                '--write-interval', '1'
            ]
            
            if channel:
                cmd.extend(['--channel', str(channel)])
            
            cmd.append(self.interface)
            
            logger.info(f"Starting scan: {' '.join(cmd)}")
            console.print(f"[yellow]📡 Ağlar taranıyor... ({duration} saniye)[/yellow]")
            
            # Start airodump-ng in background
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for scan duration
            time.sleep(duration)
            
            # Stop scan
            self.stop_scan()
            
            # Parse results
            return self.parse_scan_results(output_file)
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            console.print(f"[red]✗ Tarama hatası: {e}[/red]")
            return False
    
    def stop_scan(self):
        """Stop airodump-ng scan"""
        if self.scan_process:
            try:
                self.scan_process.terminate()
                self.scan_process.wait(timeout=5)
            except Exception:
                try:
                    self.scan_process.kill()
                except Exception:
                    pass
            self.scan_process = None
    
    def parse_scan_results(self, output_file: str) -> bool:
        """Parse airodump-ng CSV output"""
        try:
            csv_file = f"{output_file}-01.csv"
            
            if not os.path.exists(csv_file):
                logger.error(f"Scan file not found: {csv_file}")
                return False
            
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split into AP and client sections
            sections = content.split('\r\n\r\n')
            
            if len(sections) < 2:
                logger.warning("Incomplete scan data")
                return False
            
            # Parse Access Points
            ap_lines = sections[0].strip().split('\n')
            if len(ap_lines) > 1:
                # Skip header
                for line in ap_lines[1:]:
                    if line.strip():
                        self._parse_ap_line(line)
            
            # Parse Clients
            if len(sections) > 1:
                client_lines = sections[1].strip().split('\n')
                if len(client_lines) > 1:
                    # Skip header
                    for line in client_lines[1:]:
                        if line.strip():
                            self._parse_client_line(line)
            
            logger.info(f"Found {len(self.access_points)} APs and {len(self.clients)} clients")
            return True
            
        except Exception as e:
            logger.error(f"Error parsing scan results: {e}")
            return False
    
    def _parse_ap_line(self, line: str):
        """Parse access point line from CSV"""
        try:
            parts = [p.strip() for p in line.split(',')]
            
            if len(parts) < 14:
                return
            
            bssid = parts[0].strip()
            if not bssid or not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                return
            
            # Extract data
            channel_str = parts[3].strip()
            try:
                channel = int(channel_str) if channel_str.isdigit() else 0
            except:
                channel = 0
            
            power_str = parts[8].strip()
            try:
                power = int(power_str) if power_str.lstrip('-').isdigit() else -100
            except:
                power = -100
            
            beacons_str = parts[9].strip()
            try:
                beacons = int(beacons_str) if beacons_str.isdigit() else 0
            except:
                beacons = 0
            
            essid = parts[13].strip() if len(parts) > 13 else ""
            encryption = parts[5].strip() if len(parts) > 5 else "Unknown"
            
            if essid and bssid:
                ap = AccessPoint(
                    bssid=bssid.upper(),
                    essid=essid,
                    channel=channel,
                    encryption=encryption,
                    power=power,
                    beacons=beacons,
                    clients=[]
                )
                self.access_points[bssid.upper()] = ap
                
        except Exception as e:
            logger.debug(f"Error parsing AP line: {e}")
    
    def _parse_client_line(self, line: str):
        """Parse client line from CSV"""
        try:
            parts = [p.strip() for p in line.split(',')]
            
            if len(parts) < 6:
                return
            
            client_mac = parts[0].strip()
            if not client_mac or not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', client_mac):
                return
            
            bssid = parts[5].strip()
            if not bssid or bssid == '(not associated)':
                return
            
            power_str = parts[3].strip()
            try:
                power = int(power_str) if power_str.lstrip('-').isdigit() else -100
            except:
                power = -100
            
            packets_str = parts[4].strip()
            try:
                packets = int(packets_str) if packets_str.isdigit() else 0
            except:
                packets = 0
            
            client = Client(
                mac=client_mac.upper(),
                bssid=bssid.upper(),
                power=power,
                packets=packets
            )
            
            self.clients[client_mac.upper()] = client
            
            # Add client to AP's client list
            if bssid.upper() in self.access_points:
                if client_mac.upper() not in self.access_points[bssid.upper()].clients:
                    self.access_points[bssid.upper()].clients.append(client_mac.upper())
                    
        except Exception as e:
            logger.debug(f"Error parsing client line: {e}")
    
    def get_sorted_aps(self) -> List[AccessPoint]:
        """Get access points sorted by signal strength"""
        aps = list(self.access_points.values())
        # Filter out APs with no ESSID or very weak signal
        aps = [ap for ap in aps if ap.essid and ap.power > -100]
        # Sort by signal strength (strongest first)
        aps.sort(key=lambda x: x.power, reverse=True)
        return aps
    
    def get_clients_for_ap(self, bssid: str) -> List[Client]:
        """Get all clients for a specific AP"""
        clients = []
        for client in self.clients.values():
            if client.bssid.upper() == bssid.upper():
                clients.append(client)
        return clients
    
    def get_ap_by_bssid(self, bssid: str) -> Optional[AccessPoint]:
        """Get access point by BSSID"""
        return self.access_points.get(bssid.upper())
    
    def cleanup(self):
        """Clean up scan files"""
        self.stop_scan()
        cleanup_temp_files(f"{TEMP_DIR}/scan-*")

