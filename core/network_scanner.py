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
    
    def start_scan(self, channel: Optional[int] = None, duration: Optional[int] = SCAN_TIMEOUT) -> bool:
        """Start airodump-ng scan - duration=None ise sonsuz tarama"""
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
            
            # Start airodump-ng in background
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            if duration is None:
                # SONSUZ TARAMA - Kullanıcı Ctrl+C ile durduracak
                console.print(f"[yellow]📡 Ağlar taranıyor... (Sonsuz - Ctrl+C ile durdurun)[/yellow]")
                try:
                    # Process çalışırken bekle (sonsuz döngü)
                    while self.scan_process.poll() is None:
                        time.sleep(1)
                except KeyboardInterrupt:
                    console.print(f"\n[yellow]⚠️  Tarama durduruluyor...[/yellow]")
                    self.stop_scan()
            else:
                # Sınırlı süre
                console.print(f"[yellow]📡 Ağlar taranıyor... ({duration} saniye)[/yellow]")
                time.sleep(duration)
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
            
            # DEBUG: Check file existence
            console.print(f"[dim]🔍 DEBUG: CSV dosyası kontrol ediliyor: {csv_file}[/dim]")
            
            if not os.path.exists(csv_file):
                logger.error(f"Scan file not found: {csv_file}")
                console.print(f"[red]✗ CSV dosyası bulunamadı: {csv_file}[/red]")
                
                # DEBUG: List files in temp dir
                try:
                    import glob
                    files = glob.glob(f"{TEMP_DIR}/*")
                    console.print(f"[yellow]🔍 DEBUG: Temp dizinindeki dosyalar: {files}[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]🔍 DEBUG: Temp dizin okunamadı: {e}[/yellow]")
                
                return False
            
            console.print(f"[dim]✓ CSV dosyası bulundu[/dim]")
            
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            console.print(f"[dim]🔍 DEBUG: CSV boyutu: {len(content)} byte[/dim]")
            
            if len(content) < 100:
                logger.warning("CSV file too small, possibly empty")
                console.print(f"[yellow]⚠️  CSV dosyası çok küçük (boş olabilir): {len(content)} byte[/yellow]")
                return False
            
            # Split into AP and client sections
            # Try multiple delimiters
            sections = []
            
            # Try 1: \r\n\r\n (Windows)
            sections = content.split('\r\n\r\n')
            console.print(f"[dim]🔍 DEBUG: Windows format split (\\r\\n\\r\\n): {len(sections)} bölüm[/dim]")
            
            # Try 2: \n\n (Linux)
            if len(sections) < 2:
                sections = content.split('\n\n')
                console.print(f"[dim]🔍 DEBUG: Linux format split (\\n\\n): {len(sections)} bölüm[/dim]")
            
            # Try 3: Look for "Station MAC" header
            if len(sections) < 2:
                if 'Station MAC' in content:
                    parts = content.split('Station MAC')
                    if len(parts) == 2:
                        sections = [parts[0], 'Station MAC' + parts[1]]
                        console.print(f"[dim]🔍 DEBUG: 'Station MAC' split: {len(sections)} bölüm[/dim]")
            
            if len(sections) == 0:
                logger.warning("Empty scan data")
                console.print(f"[red]✗ CSV içeriği boş[/red]")
                return False
            
            # DEBUG: Show section sizes
            for i, section in enumerate(sections):
                console.print(f"[dim]🔍 DEBUG: Bölüm {i} boyutu: {len(section)} byte[/dim]")
            
            # Parse Access Points
            ap_lines = sections[0].strip().split('\n')
            console.print(f"[dim]🔍 DEBUG: AP satır sayısı: {len(ap_lines)}[/dim]")
            
            if len(ap_lines) > 1:
                # Skip header
                parsed_count = 0
                for line in ap_lines[1:]:
                    if line.strip():
                        before_count = len(self.access_points)
                        self._parse_ap_line(line)
                        if len(self.access_points) > before_count:
                            parsed_count += 1
                
                console.print(f"[dim]🔍 DEBUG: {parsed_count} AP başarıyla parse edildi[/dim]")
            
            # Parse Clients
            if len(sections) > 1:
                client_section = sections[1].strip()
                
                # DEBUG: Show first 200 chars of client section
                console.print(f"[dim]🔍 DEBUG: Client section başlangıcı: {client_section[:200]}...[/dim]")
                
                client_lines = client_section.split('\n')
                console.print(f"[dim]🔍 DEBUG: Client satır sayısı: {len(client_lines)}[/dim]")
                
                if len(client_lines) > 1:
                    # Find header line (contains "Station MAC")
                    header_idx = 0
                    for i, line in enumerate(client_lines):
                        if 'Station MAC' in line or 'station' in line.lower():
                            header_idx = i
                            console.print(f"[dim]🔍 DEBUG: Client header satırı: {i}[/dim]")
                            break
                    
                    # Parse lines after header - TÜM SATIRLARI PARSE ET
                    parsed_clients = 0
                    total_lines = 0
                    console.print(f"\n[bold cyan]{'═' * 80}[/bold cyan]")
                    console.print(f"[bold cyan]PARSING CLIENT LINES - STARTING...[/bold cyan]")
                    console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
                    
                    for line in client_lines[header_idx + 1:]:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            total_lines += 1
                            console.print(f"\n[bold yellow]>>> PARSING LINE {total_lines}:[/bold yellow]")
                            before_count = len(self.clients)
                            self._parse_client_line(line)
                            if len(self.clients) > before_count:
                                parsed_clients += 1
                    
                    console.print(f"\n[bold cyan]{'═' * 80}[/bold cyan]")
                    console.print(f"[bold cyan]PARSING COMPLETE![/bold cyan]")
                    console.print(f"[bold green]✓ {parsed_clients} new clients parsed from {total_lines} lines[/bold green]")
                    console.print(f"[bold green]✓ Total clients in database: {len(self.clients)}[/bold green]")
                    console.print(f"[bold cyan]{'═' * 80}[/bold cyan]\n")
            else:
                console.print(f"[yellow]⚠️  Client section bulunamadı (sadece 1 bölüm var)[/yellow]")
            
            logger.info(f"Found {len(self.access_points)} APs and {len(self.clients)} clients")
            console.print(f"[cyan]📊 Toplam: {len(self.access_points)} ağ, {len(self.clients)} cihaz bulundu[/cyan]")
            
            # Check if any APs were found
            if len(self.access_points) == 0:
                logger.warning("No access points found in scan")
                console.print(f"[yellow]⚠️  Hiç ağ parse edilemedi! CSV formatı kontrol ediliyor...[/yellow]")
                # DEBUG: Show first few lines
                console.print(f"[dim]🔍 DEBUG: CSV ilk 5 satır:[/dim]")
                for i, line in enumerate(ap_lines[:5]):
                    console.print(f"[dim]  {i}: {line[:100]}...[/dim]")
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
        """Parse client line from CSV - ULTRA DEBUG VERSİYON"""
        try:
            # CSV parsing - tırnak içindeki alanları dikkate al
            import csv as csv_module
            try:
                reader = csv_module.reader([line])
                parts = next(reader)
                parts = [p.strip() for p in parts]
            except:
                # Fallback: basit split
                parts = [p.strip() for p in line.split(',')]
            
            # ULTRA DEBUG - Her satırı göster
            console.print(f"[yellow]🔍 RAW LINE: {line[:150]}...[/yellow]")
            console.print(f"[yellow]🔍 PARTS COUNT: {len(parts)}[/yellow]")
            if len(parts) > 0:
                console.print(f"[yellow]🔍 PARTS[0] (MAC): '{parts[0]}'[/yellow]")
            if len(parts) > 5:
                console.print(f"[yellow]🔍 PARTS[5] (BSSID?): '{parts[5]}'[/yellow]")
            if len(parts) > 6:
                console.print(f"[yellow]🔍 PARTS[6]: '{parts[6]}'[/yellow]")
            
            if len(parts) < 6:
                console.print(f"[red]✗ Line too short: {len(parts)} parts[/red]")
                logger.debug(f"Client line too short: {len(parts)} parts")
                return
            
            client_mac = parts[0].strip()
            console.print(f"[cyan]🔍 Checking MAC: '{client_mac}'[/cyan]")
            
            if not client_mac or not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', client_mac):
                console.print(f"[red]✗ Invalid MAC format: '{client_mac}'[/red]")
                return
            
            console.print(f"[green]✓ Valid MAC: {client_mac}[/green]")
            
            # BSSID - TÜM KOLONLARI TARA!
            bssid = None
            console.print(f"[cyan]🔍 Searching for BSSID in {len(parts)} columns...[/cyan]")
            
            for idx in range(len(parts)):
                potential_bssid = parts[idx].strip()
                console.print(f"[dim]  Column {idx}: '{potential_bssid}'[/dim]")
                
                if potential_bssid and potential_bssid != '(not associated)':
                    if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', potential_bssid):
                        # Bu bir MAC adresi - ama client MAC'i mi yoksa BSSID mi?
                        if potential_bssid.upper() != client_mac.upper():
                            bssid = potential_bssid
                            console.print(f"[bold green]✓✓ BSSID FOUND at column {idx}: {bssid}[/bold green]")
                            break
            
            if not bssid:
                console.print(f"[red]✗ BSSID NOT FOUND for client {client_mac}[/red]")
                logger.debug(f"Client {client_mac} has no valid BSSID")
                return
            
            # Power ve packets
            power = -100
            packets = 0
            try:
                if len(parts) > 3:
                    power_str = parts[3].strip()
                    power = int(power_str) if power_str.lstrip('-').isdigit() else -100
                if len(parts) > 4:
                    packets_str = parts[4].strip()
                    packets = int(packets_str) if packets_str.isdigit() else 0
            except:
                pass
            
            console.print(f"[cyan]📊 Power: {power} dBm, Packets: {packets}[/cyan]")
            
            # Client oluştur
            client = Client(
                mac=client_mac.upper(),
                bssid=bssid.upper(),
                power=power,
                packets=packets
            )
            
            # Eğer zaten varsa güncelle, yoksa ekle
            if client_mac.upper() in self.clients:
                # Mevcut client'ı güncelle (daha güçlü sinyali al)
                existing = self.clients[client_mac.upper()]
                existing.power = max(existing.power, power)
                existing.packets += packets
                # BSSID değişmişse güncelle
                if bssid.upper() != existing.bssid.upper():
                    existing.bssid = bssid.upper()
                console.print(f"[yellow]⟳ Client updated: {client_mac} -> {bssid}[/yellow]")
            else:
                # Yeni client ekle
                self.clients[client_mac.upper()] = client
                console.print(f"[bold green]✓✓✓ NEW CLIENT ADDED: {client_mac} -> {bssid}[/bold green]")
                logger.info(f"✓ Client added: {client_mac} -> {bssid}")
            
            # AP'ye bağla
            if bssid.upper() in self.access_points:
                if client_mac.upper() not in self.access_points[bssid.upper()].clients:
                    self.access_points[bssid.upper()].clients.append(client_mac.upper())
                    console.print(f"[green]✓ Client linked to AP: {client_mac} -> {bssid}[/green]")
                    logger.info(f"✓ Client linked to AP: {client_mac} -> {bssid}")
            else:
                console.print(f"[red]⚠️  AP NOT FOUND: {bssid}[/red]")
                console.print(f"[yellow]Available APs: {list(self.access_points.keys())}[/yellow]")
                logger.debug(f"AP not found for client: {bssid}")
            
            console.print(f"[dim]{'─' * 80}[/dim]")
                    
        except Exception as e:
            console.print(f"[red]✗✗✗ EXCEPTION: {e}[/red]")
            logger.debug(f"Error parsing client line: {e}")
            logger.debug(f"Line content: {line[:100]}")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
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
        Seçilen ağa özel derin tarama - TÜM cihazları bulmak için!
        
        Args:
            bssid: Hedef AP'nin BSSID'si
            channel: AP'nin kanalı
            duration: Tarama süresi (saniye)
        
        Returns:
            bool: Başarılı ise True
        """
        try:
            console.print(f"\n[bold yellow]🔍 DERİN TARAMA BAŞLATILIYOR...[/bold yellow]")
            console.print(f"[cyan]📡 Hedef: {bssid}[/cyan]")
            console.print(f"[cyan]📻 Kanal: {channel}[/cyan]")
            console.print(f"[cyan]⏱️  Süre: {duration} saniye[/cyan]")
            console.print(f"[dim]💡 Bu tarama seçilen ağdaki TÜM cihazları bulacak...[/dim]\n")
            
            # Clean up old scan files
            cleanup_temp_files(f"{TEMP_DIR}/deepscan-*")
            
            output_file = f"{TEMP_DIR}/deepscan"
            
            # Build command - SADECE BU KANALI TARA!
            cmd = [
                'airodump-ng',
                '--bssid', bssid.upper(),  # SADECE BU AP!
                '--channel', str(channel),  # SADECE BU KANAL!
                '--output-format', 'csv',
                '-w', output_file,
                '--write-interval', '1',
                self.interface
            ]
            
            logger.info(f"Deep scan command: {' '.join(cmd)}")
            console.print(f"[dim]🔍 Komut: {' '.join(cmd)}[/dim]\n")
            
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
        REAL-TIME CLIENT PARSING
        CSV'yi parse et ve yeni bulunan client'ları döndür
        """
        new_clients = []
        
        try:
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
                
                # CSV parse
                cols = [c.strip() for c in line.split(',')]
                if len(cols) < 6:
                    continue
                
                client_mac = cols[0].strip().upper()
                bssid = cols[5].strip().upper()
                
                # MAC format kontrolü
                if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', client_mac):
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

