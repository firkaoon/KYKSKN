"""
KYKSKN - Network Scanner
Enhanced with PCAP-based client extraction for maximum accuracy
"""

import subprocess
import time
import csv
import os
import re
import signal
from typing import List, Dict, Optional
from dataclasses import dataclass
from rich.console import Console
from utils.helpers import run_command, cleanup_temp_files
from utils.logger import logger
from config.settings import SCAN_TIMEOUT, TEMP_DIR
from core.pcap_parser import PcapClientExtractor

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
    """Scan for wireless networks and clients with PCAP-based extraction"""
    
    def __init__(self, interface: str):
        self.interface = interface
        self.access_points: Dict[str, AccessPoint] = {}
        self.clients: Dict[str, Client] = {}  # PERSISTENT - never cleared except explicitly
        self.scan_process = None
        self.pcap_extractor = PcapClientExtractor()
        
        # Create temp directory
        os.makedirs(TEMP_DIR, exist_ok=True)
    
    def start_scan(self, channel: Optional[int] = None, duration: Optional[int] = SCAN_TIMEOUT) -> bool:
        """
        Start airodump-ng scan with PCAP capture
        
        Args:
            channel: Optional channel to scan (None = all channels)
            duration: Scan duration in seconds (None = infinite)
            
        Returns:
            bool: True if scan completed successfully
        """
        try:
            # Clean up old scan files
            cleanup_temp_files(f"{TEMP_DIR}/scan-*")
            
            output_file = f"{TEMP_DIR}/scan"
            
            # Build command - ENABLE PCAP OUTPUT
            cmd = [
                'airodump-ng',
                '--output-format', 'pcap,csv',  # BOTH PCAP AND CSV
                '-w', output_file,
                '--write-interval', '2'  # 2 seconds for better buffering
            ]
            
            if channel:
                cmd.extend(['--channel', str(channel)])
            
            cmd.append(self.interface)
            
            logger.info(f"Starting scan: {' '.join(cmd)}")
            console.print(f"[dim]🔍 Command: {' '.join(cmd)}[/dim]")
            
            # Start airodump-ng in background
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            if duration is None:
                # INFINITE SCAN - User stops with Ctrl+C
                console.print(f"[yellow]📡 Scanning networks... (Infinite - Press Ctrl+C to stop)[/yellow]")
                try:
                    # Wait while process is running
                    while self.scan_process.poll() is None:
                        time.sleep(1)
                except KeyboardInterrupt:
                    console.print(f"\n[yellow]⚠️  Stopping scan gracefully...[/yellow]")
                    self.stop_scan()
            else:
                # Limited duration
                console.print(f"[yellow]📡 Scanning networks... ({duration} seconds)[/yellow]")
                time.sleep(duration)
                
                # CRITICAL: Wait for buffer flush before stopping
                console.print(f"[dim]⏳ Waiting for buffer flush...[/dim]")
                time.sleep(3)  # Extra time for Realtek adapters
                
                self.stop_scan()
            
            # Parse results (CSV + PCAP)
            return self.parse_scan_results(output_file)
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            console.print(f"[red]✗ Scan error: {e}[/red]")
            return False
    
    def stop_scan(self):
        """
        Stop airodump-ng scan GRACEFULLY
        
        CRITICAL: Must allow time for buffer flush to disk
        Realtek adapters need extra time (up to 10 seconds)
        """
        if self.scan_process:
            try:
                logger.info("Stopping airodump-ng gracefully (SIGTERM)")
                console.print(f"[dim]⏹️  Sending SIGTERM to airodump-ng...[/dim]")
                
                # Send SIGTERM (graceful shutdown)
                self.scan_process.send_signal(signal.SIGTERM)
                
                # Wait up to 15 seconds for graceful shutdown
                # This allows airodump-ng to flush buffers properly
                try:
                    self.scan_process.wait(timeout=15)
                    logger.info("airodump-ng stopped gracefully")
                    console.print(f"[green]✓ airodump-ng stopped gracefully[/green]")
                except subprocess.TimeoutExpired:
                    # If still running after 15 seconds, force kill
                    logger.warning("airodump-ng did not stop gracefully, forcing SIGKILL")
                    console.print(f"[yellow]⚠️  Forcing SIGKILL (timeout)[/yellow]")
                    self.scan_process.kill()
                    self.scan_process.wait()
                    
            except Exception as e:
                logger.error(f"Error stopping scan: {e}")
                try:
                    self.scan_process.kill()
                except Exception:
                    pass
            finally:
                self.scan_process = None
                
                # CRITICAL: Additional wait for filesystem sync
                # Ensures CSV/PCAP files are fully written
                time.sleep(2)
    
    def parse_scan_results(self, output_file: str) -> bool:
        """
        Parse airodump-ng output (CSV + PCAP)
        
        HYBRID APPROACH:
        1. Parse CSV for AP info and basic client data
        2. Parse PCAP for ALL clients (frame-level extraction)
        3. Merge results into persistent registry
        
        Args:
            output_file: Base output filename (without extension)
            
        Returns:
            bool: True if parsing succeeded
        """
        try:
            csv_file = f"{output_file}-01.csv"
            pcap_file = f"{output_file}-01.cap"
            
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]")
            console.print(f"[bold cyan]PARSING SCAN RESULTS (CSV + PCAP)[/bold cyan]")
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
            
            # Check CSV file
            console.print(f"[dim]🔍 Checking CSV: {csv_file}[/dim]")
            
            if not os.path.exists(csv_file):
                logger.error(f"CSV file not found: {csv_file}")
                console.print(f"[red]✗ CSV file not found: {csv_file}[/red]")
                
                # DEBUG: List files in temp dir
                try:
                    import glob
                    files = glob.glob(f"{TEMP_DIR}/*")
                    console.print(f"[yellow]🔍 Temp directory contents: {files}[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]🔍 Could not read temp dir: {e}[/yellow]")
                
                return False
            
            console.print(f"[green]✓ CSV file found[/green]")
            
            # Check PCAP file
            console.print(f"[dim]🔍 Checking PCAP: {pcap_file}[/dim]")
            pcap_exists = os.path.exists(pcap_file)
            if pcap_exists:
                pcap_size = os.path.getsize(pcap_file)
                console.print(f"[green]✓ PCAP file found ({pcap_size} bytes)[/green]")
            else:
                console.print(f"[yellow]⚠️  PCAP file not found (will use CSV only)[/yellow]")
            
            # Read CSV content
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            csv_size = len(content)
            console.print(f"[dim]🔍 CSV size: {csv_size} bytes[/dim]")
            
            if csv_size < 100:
                logger.warning("CSV file too small, possibly empty")
                console.print(f"[yellow]⚠️  CSV file too small (may be empty): {csv_size} bytes[/yellow]")
                # Don't return False yet - PCAP might have data
                if not pcap_exists:
                    return False
            
            # Split into AP and client sections
            sections = []
            
            # Try multiple delimiters
            if '\r\n\r\n' in content:
                sections = content.split('\r\n\r\n')
                console.print(f"[dim]🔍 Windows format (\\r\\n\\r\\n): {len(sections)} sections[/dim]")
            elif '\n\n' in content:
                sections = content.split('\n\n')
                console.print(f"[dim]🔍 Linux format (\\n\\n): {len(sections)} sections[/dim]")
            elif 'Station MAC' in content:
                parts = content.split('Station MAC')
                if len(parts) == 2:
                    sections = [parts[0], 'Station MAC' + parts[1]]
                    console.print(f"[dim]🔍 'Station MAC' split: {len(sections)} sections[/dim]")
            
            if len(sections) == 0 and csv_size >= 100:
                logger.warning("Could not split CSV into sections")
                console.print(f"[yellow]⚠️  Could not parse CSV sections[/yellow]")
                # Continue to PCAP parsing
            
            # Show section sizes
            for i, section in enumerate(sections):
                console.print(f"[dim]🔍 Section {i}: {len(section)} bytes[/dim]")
            
            # Parse Access Points (CSV)
            csv_clients_found = 0
            
            if len(sections) > 0:
                ap_lines = sections[0].strip().split('\n')
                console.print(f"[dim]🔍 AP lines in CSV: {len(ap_lines)}[/dim]")
                
                if len(ap_lines) > 1:
                    # Skip header
                    parsed_count = 0
                    for line in ap_lines[1:]:
                        if line.strip():
                            before_count = len(self.access_points)
                            self._parse_ap_line(line)
                            if len(self.access_points) > before_count:
                                parsed_count += 1
                    
                    console.print(f"[green]✓ CSV: {parsed_count} APs parsed[/green]")
            
            # Parse Clients (CSV)
            if len(sections) > 1:
                client_section = sections[1].strip()
                
                console.print(f"[dim]🔍 Client section preview: {client_section[:200]}...[/dim]")
                
                client_lines = client_section.split('\n')
                console.print(f"[dim]🔍 Client lines in CSV: {len(client_lines)}[/dim]")
                
                if len(client_lines) > 1:
                    # Find header line (contains "Station MAC")
                    header_idx = 0
                    for i, line in enumerate(client_lines):
                        if 'Station MAC' in line or 'station' in line.lower():
                            header_idx = i
                            console.print(f"[dim]🔍 Client header at line: {i}[/dim]")
                            break
                    
                    # Parse lines after header
                    clients_before = len(self.clients)
                    console.print(f"\n[bold cyan]{'═' * 80}[/bold cyan]")
                    console.print(f"[bold cyan]PARSING CSV CLIENTS[/bold cyan]")
                    console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
                    
                    for line in client_lines[header_idx + 1:]:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self._parse_client_line(line)
                    
                    csv_clients_found = len(self.clients) - clients_before
                    console.print(f"[green]✓ CSV: {csv_clients_found} clients parsed[/green]")
                    console.print(f"[cyan]📊 Total clients in registry: {len(self.clients)}[/cyan]\n")
            else:
                console.print(f"[yellow]⚠️  No client section in CSV[/yellow]")
            
            # ═══════════════════════════════════════════════════════════════
            # PCAP PARSING - FRAME-LEVEL CLIENT EXTRACTION
            # ═══════════════════════════════════════════════════════════════
            
            pcap_clients_found = 0
            if pcap_exists and pcap_size > 0:
                console.print(f"\n[bold cyan]{'═' * 80}[/bold cyan]")
                console.print(f"[bold cyan]PARSING PCAP (FRAME-LEVEL EXTRACTION)[/bold cyan]")
                console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
                
                # Extract clients from PCAP
                pcap_clients = self.pcap_extractor.extract_clients_from_pcap(pcap_file)
                
                # Merge PCAP clients into registry
                clients_before = len(self.clients)
                for client_mac in pcap_clients:
                    if client_mac not in self.clients:
                        # New client found in PCAP but not in CSV
                        pcap_details = self.pcap_extractor.get_client_details(client_mac)
                        if pcap_details:
                            client = Client(
                                mac=client_mac,
                                bssid=pcap_details.get('bssid', '00:00:00:00:00:00'),
                                power=pcap_details.get('power', -100),
                                packets=pcap_details.get('packets', 0)
                            )
                            self.clients[client_mac] = client
                            console.print(f"[bold green]🆕 PCAP-ONLY CLIENT: {client_mac}[/bold green]")
                            logger.info(f"PCAP-only client: {client_mac}")
                    else:
                        # Client already in registry (from CSV), update packet count
                        pcap_details = self.pcap_extractor.get_client_details(client_mac)
                        if pcap_details:
                            self.clients[client_mac].packets += pcap_details.get('packets', 0)
                
                pcap_clients_found = len(self.clients) - clients_before
                console.print(f"\n[green]✓ PCAP: {pcap_clients_found} additional clients found[/green]")
                console.print(f"[bold cyan]📊 TOTAL UNIQUE CLIENTS: {len(self.clients)}[/bold cyan]\n")
            
            # ═══════════════════════════════════════════════════════════════
            # SUMMARY
            # ═══════════════════════════════════════════════════════════════
            
            console.print(f"\n[bold cyan]{'═' * 80}[/bold cyan]")
            console.print(f"[bold cyan]SCAN RESULTS SUMMARY[/bold cyan]")
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]")
            console.print(f"[cyan]📡 Access Points: {len(self.access_points)}[/cyan]")
            console.print(f"[cyan]👥 Clients (CSV): {csv_clients_found}[/cyan]")
            console.print(f"[cyan]📦 Clients (PCAP): {pcap_clients_found}[/cyan]")
            console.print(f"[bold green]✓ TOTAL UNIQUE CLIENTS: {len(self.clients)}[/bold green]")
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
            
            logger.info(f"Scan complete: {len(self.access_points)} APs, {len(self.clients)} clients (CSV: {csv_clients_found}, PCAP: {pcap_clients_found})")
            
            # Check if any APs were found
            if len(self.access_points) == 0:
                logger.warning("No access points found in scan")
                console.print(f"[yellow]⚠️  No APs found - check adapter and environment[/yellow]")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error parsing scan results: {e}")
            console.print(f"[red]✗ CSV parse hatası: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return False
    
    def _parse_ap_line(self, line: str):
        """Parse access point line from CSV"""
        try:
            parts = [p.strip() for p in line.split(',')]
            
            if len(parts) < 14:
                logger.debug(f"AP line too short: {len(parts)} parts (need 14)")
                return
            
            bssid = parts[0].strip()
            if not bssid or not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                logger.debug(f"Invalid BSSID format: {bssid}")
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
            
            # DEBUG: Log what we're parsing
            console.print(f"[dim]🔍 Parsing AP: BSSID={bssid}, ESSID={essid}, Channel={channel}, Power={power}[/dim]")
            logger.info(f"Parsing AP: BSSID={bssid}, ESSID={essid}")
            
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
                console.print(f"[green]✓ AP added: {essid} ({bssid.upper()})[/green]")
                logger.info(f"✓ AP added: {essid} ({bssid})")
            else:
                console.print(f"[yellow]⚠️  AP skipped: ESSID={essid}, BSSID={bssid}[/yellow]")
                logger.info(f"AP skipped: ESSID={essid}, BSSID={bssid}")
                
        except Exception as e:
            logger.debug(f"Error parsing AP line: {e}")
            logger.debug(f"Line content: {line[:100]}")
    
    def _parse_client_line(self, line: str):
        """
        Parse client line from CSV - ACCUMULATIVE (never overwrites)
        
        PERSISTENT REGISTRY LOGIC:
        - If client exists: UPDATE power (max), ADD packets (accumulate), update BSSID if changed
        - If client is new: ADD to registry
        - NEVER delete or reset clients
        """
        try:
            # CSV parsing
            import csv as csv_module
            reader = csv_module.reader([line])
            parts = next(reader)
            parts = [p.strip() for p in parts]
            
            # Minimum 6 columns required
            if len(parts) < 6:
                logger.debug(f"Client line too short: {len(parts)} parts")
                return
            
            # CSV FORMAT (FIXED):
            # 0: Station MAC
            # 1: First time seen
            # 2: Last time seen
            # 3: Power
            # 4: # packets
            # 5: BSSID
            # 6: Probed ESSIDs
            
            client_mac = parts[0].strip().upper()
            bssid = parts[5].strip().upper()
            
            # MAC format validation
            if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', client_mac):
                logger.debug(f"Invalid client MAC: {client_mac}")
                return
            
            # BSSID format validation
            if not bssid or bssid == '(NOT ASSOCIATED)':
                logger.debug(f"Client {client_mac} not associated")
                return
            
            if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                logger.debug(f"Invalid BSSID: {bssid}")
                return
            
            # Parse power and packets
            power = -100
            packets = 0
            try:
                power_str = parts[3].strip()
                power = int(power_str) if power_str.lstrip('-').isdigit() else -100
            except:
                pass
            
            try:
                packets_str = parts[4].strip()
                packets = int(packets_str) if packets_str.isdigit() else 0
            except:
                pass
            
            # PERSISTENT REGISTRY: Update or add
            if client_mac in self.clients:
                # UPDATE existing client (accumulate data)
                existing = self.clients[client_mac]
                existing.power = max(existing.power, power)  # Keep strongest signal
                existing.packets += packets  # Accumulate packets
                if bssid != existing.bssid:
                    existing.bssid = bssid  # Update if roamed
                console.print(f"[yellow]⟳ Client updated: {client_mac} -> {bssid} ({power} dBm, +{packets} pkts)[/yellow]")
                logger.debug(f"Client updated: {client_mac}")
            else:
                # ADD new client to registry
                client = Client(
                    mac=client_mac,
                    bssid=bssid,
                    power=power,
                    packets=packets
                )
                self.clients[client_mac] = client
                console.print(f"[bold green]✓ NEW CLIENT (CSV): {client_mac} -> {bssid} ({power} dBm, {packets} pkts)[/bold green]")
                logger.info(f"New client added: {client_mac} -> {bssid}")
            
            # Link to AP
            if bssid in self.access_points:
                if client_mac not in self.access_points[bssid].clients:
                    self.access_points[bssid].clients.append(client_mac)
                    logger.debug(f"Client linked to AP: {client_mac} -> {bssid}")
            else:
                logger.debug(f"AP not found for client: {bssid}")
                    
        except Exception as e:
            logger.debug(f"Error parsing client line: {e}")
            logger.debug(f"Line: {line[:100]}")
    
    def get_sorted_aps(self) -> List[AccessPoint]:
        """Get access points sorted by signal strength"""
        aps = list(self.access_points.values())
        console.print(f"[dim]🔍 DEBUG: get_sorted_aps - Toplam {len(aps)} ağ[/dim]")
        
        # Filter out APs with no ESSID or very weak signal
        aps = [ap for ap in aps if ap.essid and ap.power > -100]
        console.print(f"[dim]🔍 DEBUG: Filtreleme sonrası {len(aps)} ağ (ESSID var ve sinyal > -100)[/dim]")
        
        # Sort by signal strength (strongest first)
        aps.sort(key=lambda x: x.power, reverse=True)
        return aps
    
    def get_clients_for_ap(self, bssid: str) -> List[Client]:
        """Get all clients for a specific AP"""
        clients = []
        bssid_upper = bssid.upper()
        
        console.print(f"[cyan]🔍 Getting clients for AP: {bssid_upper}[/cyan]")
        console.print(f"[cyan]🔍 Total clients in database: {len(self.clients)}[/cyan]")
        logger.info(f"Getting clients for AP: {bssid_upper}")
        logger.info(f"Total clients in database: {len(self.clients)}")
        
        for client in self.clients.values():
            console.print(f"[dim]  Checking: {client.mac} -> {client.bssid} (looking for {bssid_upper})[/dim]")
            logger.info(f"Checking client: {client.mac} -> {client.bssid} (looking for {bssid_upper})")
            
            if client.bssid.upper() == bssid_upper:
                clients.append(client)
                console.print(f"[green]  ✓ MATCH! Client {client.mac} belongs to this AP[/green]")
                logger.info(f"✓ Client matched: {client.mac}")
            else:
                console.print(f"[yellow]  ✗ No match: {client.bssid} != {bssid_upper}[/yellow]")
        
        console.print(f"[bold cyan]📊 Found {len(clients)} clients for {bssid_upper}[/bold cyan]")
        logger.info(f"Found {len(clients)} clients for {bssid_upper}")
        return clients
    
    def deep_scan_ap(self, bssid: str, channel: int, duration: int = 30) -> bool:
        """
        Deep scan for specific AP - finds ALL clients
        
        CRITICAL: Uses PCAP + CSV hybrid approach
        PERSISTENT: Accumulates clients, never resets registry
        
        Args:
            bssid: Target AP BSSID
            channel: AP channel
            duration: Scan duration in seconds
        
        Returns:
            bool: True if successful
        """
        try:
            console.print(f"\n[bold yellow]🔍 DEEP SCAN STARTING...[/bold yellow]")
            console.print(f"[cyan]📡 Target: {bssid}[/cyan]")
            console.print(f"[cyan]📻 Channel: {channel}[/cyan]")
            console.print(f"[cyan]⏱️  Duration: {duration} seconds[/cyan]")
            console.print(f"[dim]💡 This scan will find ALL clients on this network...[/dim]\n")
            
            # Clean up old scan files
            cleanup_temp_files(f"{TEMP_DIR}/deepscan-*")
            
            output_file = f"{TEMP_DIR}/deepscan"
            
            # Build command - ENABLE PCAP + CSV
            cmd = [
                'airodump-ng',
                '--bssid', bssid.upper(),  # Filter to this AP only
                '--channel', str(channel),  # Lock to this channel
                '--output-format', 'pcap,csv',  # BOTH formats
                '-w', output_file,
                '--write-interval', '2',  # 2 seconds for better buffering
                self.interface
            ]
            
            logger.info(f"Deep scan command: {' '.join(cmd)}")
            console.print(f"[dim]🔍 Command: {' '.join(cmd)}[/dim]\n")
            
            # Start airodump-ng
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Progress bar
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
            
            # REAL-TIME MONITORING - Her 3 saniyede CSV'yi parse et ve yeni client'ları göster
            seen_clients = set()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"[cyan]Cihazlar aranıyor (REAL-TIME)...", total=duration)
                
                for i in range(duration):
                    time.sleep(1)
                    progress.update(task, advance=1)
                    
                    # Her 2 saniyede bir REAL-TIME parse (daha sık kontrol)
                    if (i + 1) % 2 == 0:
                        temp_csv = f"{output_file}-01.csv"
                        if os.path.exists(temp_csv):
                            # Parse CSV ve yeni client'ları bul
                            new_clients = self._parse_clients_realtime(temp_csv, bssid.upper(), seen_clients)
                            
                            if new_clients:
                                for client_mac in new_clients:
                                    progress.console.print(f"[bold green]🆕 YENİ CİHAZ BULUNDU: {client_mac}[/bold green]")
                                    seen_clients.add(client_mac)
                            
                            # Toplam sayıyı göster
                            total_count = len(seen_clients)
                            progress.console.print(f"[cyan]📊 {i+1}s: Toplam {total_count} cihaz[/cyan]")
            
            # Stop scan
            self.stop_scan()
            
            console.print(f"\n[green]✓ Derin tarama tamamlandı![/green]")
            console.print(f"[bold cyan]📊 REAL-TIME: {len(seen_clients)} cihaz bulundu[/bold cyan]\n")
            
            # Parse results - ÖNCEKİ CLIENT'LARI TEMİZLE!
            old_client_count = len(self.clients)
            
            # Sadece bu AP'ye ait client'ları temizle
            clients_to_remove = [mac for mac, client in self.clients.items() if client.bssid.upper() == bssid.upper()]
            for mac in clients_to_remove:
                del self.clients[mac]
            
            console.print(f"[dim]🔄 Eski client'lar temizlendi: {len(clients_to_remove)} adet[/dim]")
            
            # Parse new results
            csv_file = f"{output_file}-01.csv"
            console.print(f"[dim]🔍 CSV dosyası: {csv_file}[/dim]")
            
            # CSV içeriğini göster (debug)
            if os.path.exists(csv_file):
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                console.print(f"[dim]🔍 CSV boyutu: {len(content)} byte[/dim]")
                
                # Client satırlarını say
                if 'Station MAC' in content:
                    client_section = content.split('Station MAC')[1] if len(content.split('Station MAC')) > 1 else ""
                    client_lines = [line for line in client_section.split('\n') if line.strip() and not line.startswith('#')]
                    console.print(f"[bold yellow]🔍 CSV'de {len(client_lines)-1} client satırı var (header hariç)[/bold yellow]")
            
            success = self.parse_scan_results(output_file)
            
            if success:
                new_client_count = len([c for c in self.clients.values() if c.bssid.upper() == bssid.upper()])
                console.print(f"[bold green]✓ {new_client_count} cihaz bulundu![/bold green]\n")
            
            return success
            
        except Exception as e:
            logger.error(f"Deep scan error: {e}")
            console.print(f"[red]✗ Derin tarama hatası: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return False
    
    def _parse_clients_realtime(self, csv_file: str, target_bssid: str, seen_clients: set) -> list:
        """
        REAL-TIME CLIENT PARSING - DOĞRU VERSİYON
        CSV'yi parse et ve yeni bulunan client'ları döndür
        """
        new_clients = []
        
        try:
            import csv as csv_module
            
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Client section'ı bul
            if 'Station MAC' not in content:
                return new_clients
            
            parts = content.split('Station MAC')
            if len(parts) < 2:
                return new_clients
            
            client_section = parts[1]
            lines = client_section.strip().split('\n')
            
            # Her satırı parse et
            for line in lines[1:]:  # İlk satır header
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    # CSV parse (tırnak desteği)
                    reader = csv_module.reader([line])
                    cols = next(reader)
                    cols = [c.strip() for c in cols]
                    
                    if len(cols) < 6:
                        continue
                    
                    # SABİT INDEX
                    client_mac = cols[0].strip().upper()
                    bssid = cols[5].strip().upper()
                    
                    # MAC format kontrolü
                    if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', client_mac):
                        continue
                    
                    # BSSID format kontrolü
                    if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                        continue
                    
                    # BSSID kontrolü
                    if bssid != target_bssid.upper():
                        continue
                    
                    # Yeni client mi?
                    if client_mac not in seen_clients:
                        new_clients.append(client_mac)
                        
                        # Hemen database'e ekle
                        try:
                            power = int(cols[3].strip()) if cols[3].strip().lstrip('-').isdigit() else -100
                        except:
                            power = -100
                        
                        try:
                            packets = int(cols[4].strip()) if cols[4].strip().isdigit() else 0
                        except:
                            packets = 0
                        
                        client = Client(
                            mac=client_mac,
                            bssid=bssid,
                            power=power,
                            packets=packets
                        )
                        
                        self.clients[client_mac] = client
                        
                        # AP'ye bağla
                        if bssid in self.access_points:
                            if client_mac not in self.access_points[bssid].clients:
                                self.access_points[bssid].clients.append(client_mac)
                
                except Exception as line_error:
                    logger.debug(f"Error parsing line: {line_error}")
                    continue
            
            return new_clients
            
        except Exception as e:
            logger.debug(f"Error in real-time parse: {e}")
            return new_clients
    
    def _count_clients_in_csv(self, csv_file: str, bssid: str) -> int:
        """CSV'deki client sayısını hızlıca say (progress için)"""
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Client section'ı bul
            if 'Station MAC' in content:
                client_section = content.split('Station MAC')[1] if 'Station MAC' in content else ""
                # BSSID'yi içeren satırları say
                count = content.count(bssid)
                return max(0, count - 1)  # Header'ı çıkar
            return 0
        except:
            return 0
    
    def get_ap_by_bssid(self, bssid: str) -> Optional[AccessPoint]:
        """Get access point by BSSID"""
        return self.access_points.get(bssid.upper())
    
    def cleanup(self):
        """Clean up scan files"""
        self.stop_scan()
        cleanup_temp_files(f"{TEMP_DIR}/scan-*")
        cleanup_temp_files(f"{TEMP_DIR}/deepscan-*")

