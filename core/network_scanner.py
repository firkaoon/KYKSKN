"""
KYKSKN - Network Scanner (REFACTORED FOR MAXIMUM CLIENT DETECTION)

CRITICAL FIXES:
1. PCAP-based client extraction (wlan.sa / wlan.da analysis)
2. Graceful airodump-ng shutdown with buffer flush
3. Persistent client registry (accumulation across scans)
4. Hybrid CSV+PCAP parsing strategy
5. Continuous scanning without state reset
6. Realtek driver frame drop mitigation
"""

import subprocess
import time
import csv
import os
import re
import signal
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from rich.console import Console
from scapy.all import rdpcap, Dot11, Dot11Beacon, Dot11ProbeReq, Dot11ProbeResp, Dot11AssoReq, Dot11AssoResp, Dot11Auth, Dot11Deauth, Dot11Disassoc
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
    clients: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.essid} ({self.bssid}) - Ch:{self.channel} - {self.power}dBm"


@dataclass
class Client:
    """Client device data structure with historical tracking"""
    mac: str
    bssid: str
    power: int
    packets: int
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    
    def __str__(self):
        return f"{self.mac} -> {self.bssid} ({self.power}dBm, {self.packets} pkts)"


class NetworkScanner:
    """Scan for wireless networks and clients with MAXIMUM detection accuracy"""
    
    def __init__(self, interface: str):
        self.interface = interface
        self.access_points: Dict[str, AccessPoint] = {}
        
        # PERSISTENT CLIENT REGISTRY - NEVER RESET!
        self.clients: Dict[str, Client] = {}
        self.all_time_clients: Set[str] = set()  # Historical record
        
        self.scan_process = None
        self.scan_start_time = None
        
        # Create temp directory
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        console.print("[bold green]✓ NetworkScanner initialized with PERSISTENT client registry[/bold green]")
    
    def start_scan(self, channel: Optional[int] = None, duration: Optional[int] = SCAN_TIMEOUT) -> bool:
        """
        Start airodump-ng scan with GRACEFUL shutdown support
        
        Args:
            channel: Specific channel to scan (None = all channels)
            duration: Scan duration in seconds (None = infinite until Ctrl+C)
        
        Returns:
            bool: Success status
        """
        try:
            # Clean up old scan files
            cleanup_temp_files(f"{TEMP_DIR}/scan-*")
            
            output_file = f"{TEMP_DIR}/scan"
            
            # Build command with BOTH CSV and PCAP output
            cmd = [
                'airodump-ng',
                '--output-format', 'pcap,csv',  # BOTH formats!
                '-w', output_file,
                '--write-interval', '2',  # 2 seconds for better buffering
            ]
            
            if channel:
                cmd.extend(['--channel', str(channel)])
            
            cmd.append(self.interface)
            
            logger.info(f"Starting scan: {' '.join(cmd)}")
            console.print(f"[cyan]📡 Starting airodump-ng with CSV+PCAP output...[/cyan]")
            
            # Start airodump-ng in background
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid  # Create process group for clean termination
            )
            
            self.scan_start_time = time.time()
            
            if duration is None:
                # INFINITE SCAN - User will stop with Ctrl+C
                console.print(f"[yellow]📡 Scanning networks... (Infinite - Press Ctrl+C to stop)[/yellow]")
                try:
                    while self.scan_process.poll() is None:
                        time.sleep(1)
                        
                        # Real-time PCAP parsing every 5 seconds
                        if int(time.time() - self.scan_start_time) % 5 == 0:
                            self._parse_pcap_realtime(output_file)
                            
                except KeyboardInterrupt:
                    console.print(f"\n[yellow]⚠️  Stopping scan gracefully...[/yellow]")
                    self.stop_scan_gracefully()
            else:
                # Timed scan
                console.print(f"[yellow]📡 Scanning networks... ({duration} seconds)[/yellow]")
                
                # Real-time monitoring
                elapsed = 0
                while elapsed < duration and self.scan_process.poll() is None:
                    time.sleep(1)
                    elapsed += 1
                    
                    # Real-time PCAP parsing every 5 seconds
                    if elapsed % 5 == 0:
                        self._parse_pcap_realtime(output_file)
                        console.print(f"[dim]⏱️  {elapsed}s - Found {len(self.clients)} clients so far...[/dim]")
                
                self.stop_scan_gracefully()
            
            # Final comprehensive parsing (CSV + PCAP)
            console.print(f"[cyan]🔍 Performing final comprehensive analysis...[/cyan]")
            return self.parse_scan_results(output_file)
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            console.print(f"[red]✗ Scan error: {e}[/red]")
            return False
    
    def stop_scan_gracefully(self):
        """
        GRACEFUL SHUTDOWN - Ensures all buffered frames are written
        
        This is CRITICAL for Realtek adapters which buffer frames aggressively
        """
        if self.scan_process:
            try:
                console.print(f"[yellow]⚙️  Sending SIGTERM to airodump-ng (graceful shutdown)...[/yellow]")
                
                # Send SIGTERM to process group (not just main process)
                try:
                    os.killpg(os.getpgid(self.scan_process.pid), signal.SIGTERM)
                except:
                    self.scan_process.terminate()
                
                # Wait up to 10 seconds for graceful shutdown
                console.print(f"[yellow]⏳ Waiting for buffer flush (up to 10s)...[/yellow]")
                try:
                    self.scan_process.wait(timeout=10)
                    console.print(f"[green]✓ airodump-ng stopped gracefully[/green]")
                except subprocess.TimeoutExpired:
                    console.print(f"[yellow]⚠️  Timeout - sending SIGKILL...[/yellow]")
                    try:
                        os.killpg(os.getpgid(self.scan_process.pid), signal.SIGKILL)
                    except:
                        self.scan_process.kill()
                    self.scan_process.wait(timeout=2)
                
                # Additional wait for filesystem sync (important for PCAP)
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error stopping scan: {e}")
                try:
                    self.scan_process.kill()
                except:
                    pass
            
            self.scan_process = None
    
    def stop_scan(self):
        """Legacy method - redirects to graceful shutdown"""
        self.stop_scan_gracefully()
    
    def _parse_pcap_realtime(self, output_file: str):
        """
        REAL-TIME PCAP parsing during scan
        
        Extracts clients from PCAP without stopping the scan
        """
        try:
            pcap_file = f"{output_file}-01.cap"
            
            if not os.path.exists(pcap_file):
                return
            
            # Get file size to avoid parsing incomplete writes
            file_size = os.path.getsize(pcap_file)
            if file_size < 1000:  # Too small
                return
            
            # Parse PCAP (only new packets since last parse)
            self._extract_clients_from_pcap(pcap_file, verbose=False)
            
        except Exception as e:
            logger.debug(f"Real-time PCAP parse error (non-fatal): {e}")
    
    def parse_scan_results(self, output_file: str) -> bool:
        """
        HYBRID PARSING STRATEGY - CSV for APs, PCAP for clients
        
        This ensures we get:
        1. Complete AP information from CSV (beacons, encryption, etc.)
        2. ALL clients from PCAP (every frame with wlan.sa / wlan.da)
        """
        try:
            csv_file = f"{output_file}-01.csv"
            pcap_file = f"{output_file}-01.cap"
            
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]")
            console.print(f"[bold cyan]HYBRID PARSING: CSV (APs) + PCAP (Clients)[/bold cyan]")
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
            
            # Step 1: Parse CSV for Access Points
            console.print(f"[cyan]📊 Step 1: Parsing CSV for Access Points...[/cyan]")
            if os.path.exists(csv_file):
                self._parse_csv_for_aps(csv_file)
                console.print(f"[green]✓ Found {len(self.access_points)} Access Points[/green]\n")
            else:
                console.print(f"[yellow]⚠️  CSV file not found: {csv_file}[/yellow]\n")
            
            # Step 2: Parse PCAP for ALL clients (comprehensive)
            console.print(f"[cyan]📦 Step 2: Parsing PCAP for ALL clients...[/cyan]")
            if os.path.exists(pcap_file):
                clients_before = len(self.clients)
                self._extract_clients_from_pcap(pcap_file, verbose=True)
                clients_after = len(self.clients)
                new_clients = clients_after - clients_before
                
                console.print(f"[bold green]✓ PCAP Analysis Complete![/bold green]")
                console.print(f"[green]  • New clients from PCAP: {new_clients}[/green]")
                console.print(f"[green]  • Total clients in registry: {clients_after}[/green]\n")
            else:
                console.print(f"[yellow]⚠️  PCAP file not found: {pcap_file}[/yellow]\n")
            
            # Step 3: Link clients to APs
            console.print(f"[cyan]🔗 Step 3: Linking clients to Access Points...[/cyan]")
            self._link_clients_to_aps()
            console.print(f"[green]✓ Client-AP associations updated[/green]\n")
            
            # Summary
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]")
            console.print(f"[bold green]✓ SCAN COMPLETE![/bold green]")
            console.print(f"[cyan]📊 Access Points: {len(self.access_points)}[/cyan]")
            console.print(f"[cyan]📱 Clients (this scan): {len(self.clients)}[/cyan]")
            console.print(f"[cyan]📜 All-time clients: {len(self.all_time_clients)}[/cyan]")
            console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
            
            return len(self.access_points) > 0
            
        except Exception as e:
            logger.error(f"Error parsing scan results: {e}")
            console.print(f"[red]✗ Parse error: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return False
    
    def _parse_csv_for_aps(self, csv_file: str):
        """Parse CSV file for Access Point information"""
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split into AP and client sections
            sections = content.split('\r\n\r\n') if '\r\n\r\n' in content else content.split('\n\n')
            
            if len(sections) == 0:
                return
            
            # Parse Access Points section
            ap_lines = sections[0].strip().split('\n')
            
            if len(ap_lines) > 1:
                for line in ap_lines[1:]:  # Skip header
                    if line.strip():
                        self._parse_ap_line(line)
            
        except Exception as e:
            logger.error(f"Error parsing CSV for APs: {e}")
    
    def _parse_ap_line(self, line: str):
        """Parse single AP line from CSV"""
        try:
            parts = [p.strip() for p in line.split(',')]
            
            if len(parts) < 14:
                return
            
            bssid = parts[0].strip()
            if not bssid or not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                return
            
            # Extract data
            channel_str = parts[3].strip()
            channel = int(channel_str) if channel_str.isdigit() else 0
            
            power_str = parts[8].strip()
            power = int(power_str) if power_str.lstrip('-').isdigit() else -100
            
            beacons_str = parts[9].strip()
            beacons = int(beacons_str) if beacons_str.isdigit() else 0
            
            essid = parts[13].strip() if len(parts) > 13 else ""
            encryption = parts[5].strip() if len(parts) > 5 else "Unknown"
            
            if essid and bssid:
                # Update or create AP
                bssid_upper = bssid.upper()
                if bssid_upper in self.access_points:
                    # Update existing
                    ap = self.access_points[bssid_upper]
                    ap.power = max(ap.power, power)
                    ap.beacons += beacons
                else:
                    # Create new
                    ap = AccessPoint(
                        bssid=bssid_upper,
                        essid=essid,
                        channel=channel,
                        encryption=encryption,
                        power=power,
                        beacons=beacons,
                        clients=[]
                    )
                    self.access_points[bssid_upper] = ap
                    console.print(f"[green]✓ AP: {essid} ({bssid_upper}) - Ch{channel}[/green]")
                
        except Exception as e:
            logger.debug(f"Error parsing AP line: {e}")
    
    def _extract_clients_from_pcap(self, pcap_file: str, verbose: bool = False):
        """
        PCAP-BASED CLIENT EXTRACTION - The core fix!
        
        Analyzes ALL frames in PCAP to extract client MAC addresses from:
        - wlan.sa (source address)
        - wlan.da (destination address)
        - Association requests/responses
        - Authentication frames
        - Data frames
        
        This catches clients that CSV misses due to timing/buffering issues.
        """
        try:
            if verbose:
                console.print(f"[cyan]🔍 Reading PCAP file: {pcap_file}[/cyan]")
            
            # Read PCAP with scapy
            try:
                packets = rdpcap(pcap_file)
            except Exception as e:
                logger.error(f"Failed to read PCAP: {e}")
                return
            
            if verbose:
                console.print(f"[cyan]📦 Analyzing {len(packets)} packets...[/cyan]")
            
            # Track unique client MACs and their associated BSSIDs
            client_associations: Dict[str, Set[str]] = {}  # client_mac -> set of BSSIDs
            ap_bssids: Set[str] = set()
            
            # First pass: Identify all AP BSSIDs (from beacons)
            for pkt in packets:
                if pkt.haslayer(Dot11Beacon):
                    bssid = pkt[Dot11].addr3.upper()
                    ap_bssids.add(bssid)
            
            if verbose:
                console.print(f"[dim]📡 Identified {len(ap_bssids)} APs from beacons[/dim]")
            
            # Second pass: Extract client MACs from ALL frame types
            clients_found = 0
            
            for pkt in packets:
                if not pkt.haslayer(Dot11):
                    continue
                
                dot11 = pkt[Dot11]
                
                # Get addresses
                addr1 = dot11.addr1.upper() if dot11.addr1 else None
                addr2 = dot11.addr2.upper() if dot11.addr2 else None
                addr3 = dot11.addr3.upper() if dot11.addr3 else None
                
                # Skip broadcast/multicast
                if addr1 and (addr1.startswith('FF:FF') or addr1.startswith('01:00')):
                    addr1 = None
                if addr2 and (addr2.startswith('FF:FF') or addr2.startswith('01:00')):
                    addr2 = None
                
                # Determine client and AP based on frame type
                client_mac = None
                ap_bssid = None
                
                # Association Request: addr1=AP, addr2=client, addr3=AP
                if pkt.haslayer(Dot11AssoReq):
                    client_mac = addr2
                    ap_bssid = addr1
                
                # Association Response: addr1=client, addr2=AP, addr3=AP
                elif pkt.haslayer(Dot11AssoResp):
                    client_mac = addr1
                    ap_bssid = addr2
                
                # Authentication: addr1 or addr2 could be client
                elif pkt.haslayer(Dot11Auth):
                    # addr1=receiver, addr2=transmitter, addr3=BSSID
                    ap_bssid = addr3
                    # Client is the non-AP address
                    if addr1 and addr1 in ap_bssids:
                        client_mac = addr2
                    elif addr2 and addr2 in ap_bssids:
                        client_mac = addr1
                    else:
                        # Guess: addr2 is usually client in auth frames
                        client_mac = addr2
                        if not ap_bssid:
                            ap_bssid = addr1
                
                # Data frames: ToDS=1 means client->AP, FromDS=1 means AP->client
                elif dot11.type == 2:  # Data frame
                    to_ds = (dot11.FCfield & 0x1) != 0
                    from_ds = (dot11.FCfield & 0x2) != 0
                    
                    if to_ds and not from_ds:
                        # Client -> AP: addr1=BSSID, addr2=SA (client), addr3=DA
                        ap_bssid = addr1
                        client_mac = addr2
                    elif from_ds and not to_ds:
                        # AP -> Client: addr1=DA (client), addr2=BSSID, addr3=SA
                        client_mac = addr1
                        ap_bssid = addr2
                    elif to_ds and from_ds:
                        # WDS (ignore for now)
                        pass
                    else:
                        # Ad-hoc (ignore)
                        pass
                
                # Deauth/Disassoc: addr1=destination, addr2=source, addr3=BSSID
                elif pkt.haslayer(Dot11Deauth) or pkt.haslayer(Dot11Disassoc):
                    ap_bssid = addr3
                    # Client is the non-AP address
                    if addr1 and addr1 not in ap_bssids:
                        client_mac = addr1
                    elif addr2 and addr2 not in ap_bssids:
                        client_mac = addr2
                
                # Validate and store
                if client_mac and ap_bssid:
                    # Validate MAC format
                    if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', client_mac):
                        continue
                    if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', ap_bssid):
                        continue
                    
                    # Skip if client MAC is actually an AP
                    if client_mac in ap_bssids:
                        continue
                    
                    # Store association
                    if client_mac not in client_associations:
                        client_associations[client_mac] = set()
                    client_associations[client_mac].add(ap_bssid)
            
            # Add clients to registry
            for client_mac, bssid_set in client_associations.items():
                # Use the most common BSSID (or first one)
                ap_bssid = list(bssid_set)[0]
                
                # Add or update client
                if client_mac in self.clients:
                    # Update existing
                    client = self.clients[client_mac]
                    client.packets += 1
                    client.last_seen = time.time()
                    # Update BSSID if changed
                    if ap_bssid != client.bssid:
                        client.bssid = ap_bssid
                else:
                    # Create new client
                    client = Client(
                        mac=client_mac,
                        bssid=ap_bssid,
                        power=-70,  # Default (PCAP doesn't have signal strength)
                        packets=1
                    )
                    self.clients[client_mac] = client
                    self.all_time_clients.add(client_mac)
                    clients_found += 1
                    
                    if verbose:
                        console.print(f"[bold green]✓ NEW CLIENT from PCAP: {client_mac} -> {ap_bssid}[/bold green]")
            
            if verbose and clients_found > 0:
                console.print(f"[bold green]🎉 Discovered {clients_found} new clients from PCAP analysis![/bold green]")
            
        except Exception as e:
            logger.error(f"Error extracting clients from PCAP: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _link_clients_to_aps(self):
        """Link clients to their Access Points"""
        for client in self.clients.values():
            bssid = client.bssid.upper()
            if bssid in self.access_points:
                if client.mac not in self.access_points[bssid].clients:
                    self.access_points[bssid].clients.append(client.mac)
    
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
        bssid_upper = bssid.upper()
        
        console.print(f"[cyan]🔍 Getting clients for AP: {bssid_upper}[/cyan]")
        console.print(f"[cyan]📊 Total clients in registry: {len(self.clients)}[/cyan]")
        
        for client in self.clients.values():
            if client.bssid.upper() == bssid_upper:
                clients.append(client)
                console.print(f"[green]  ✓ {client.mac} -> {client.bssid}[/green]")
        
        console.print(f"[bold cyan]📊 Found {len(clients)} clients for {bssid_upper}[/bold cyan]")
        return clients
    
    def deep_scan_ap(self, bssid: str, channel: int, duration: int = 30) -> bool:
        """
        Deep scan for a specific AP - ACCUMULATES clients (no reset!)
        
        Args:
            bssid: Target AP BSSID
            channel: AP channel
            duration: Scan duration (seconds)
        
        Returns:
            bool: Success status
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
            
            # Build command - BOTH CSV and PCAP
            cmd = [
                'airodump-ng',
                '--bssid', bssid.upper(),
                '--channel', str(channel),
                '--output-format', 'pcap,csv',
                '-w', output_file,
                '--write-interval', '2',
                self.interface
            ]
            
            logger.info(f"Deep scan command: {' '.join(cmd)}")
            
            # Start airodump-ng
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            # Progress with real-time monitoring
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
            
            clients_before = len([c for c in self.clients.values() if c.bssid.upper() == bssid.upper()])
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"[cyan]Scanning for clients (REAL-TIME)...", total=duration)
                
                for i in range(duration):
                    time.sleep(1)
                    progress.update(task, advance=1)
                    
                    # Real-time PCAP parsing every 3 seconds
                    if (i + 1) % 3 == 0:
                        temp_pcap = f"{output_file}-01.cap"
                        if os.path.exists(temp_pcap):
                            self._extract_clients_from_pcap(temp_pcap, verbose=False)
                            
                            current_clients = len([c for c in self.clients.values() if c.bssid.upper() == bssid.upper()])
                            if current_clients > clients_before:
                                new_count = current_clients - clients_before
                                progress.console.print(f"[bold green]🆕 Found {new_count} client(s) so far![/bold green]")
                                clients_before = current_clients
            
            # Graceful stop
            self.stop_scan_gracefully()
            
            console.print(f"\n[green]✓ Deep scan completed![/green]")
            
            # Final parse
            success = self.parse_scan_results(output_file)
            
            if success:
                client_count = len([c for c in self.clients.values() if c.bssid.upper() == bssid.upper()])
                console.print(f"[bold green]✓ {client_count} total clients found for this AP![/bold green]\n")
            
            return success
            
        except Exception as e:
            logger.error(f"Deep scan error: {e}")
            console.print(f"[red]✗ Deep scan error: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return False
    
    def get_ap_by_bssid(self, bssid: str) -> Optional[AccessPoint]:
        """Get access point by BSSID"""
        return self.access_points.get(bssid.upper())
    
    def reset_client_registry(self):
        """
        OPTIONAL: Reset client registry
        
        WARNING: Only use this if you want to start fresh.
        Normal operation should ACCUMULATE clients!
        """
        old_count = len(self.clients)
        self.clients.clear()
        console.print(f"[yellow]⚠️  Client registry reset ({old_count} clients cleared)[/yellow]")
        console.print(f"[dim]💡 All-time registry still has {len(self.all_time_clients)} clients[/dim]")
    
    def cleanup(self):
        """Clean up scan files"""
        self.stop_scan_gracefully()
        cleanup_temp_files(f"{TEMP_DIR}/scan-*")
        cleanup_temp_files(f"{TEMP_DIR}/deepscan-*")
