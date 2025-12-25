"""
KYKSKN - Interactive Menus
"""

import questionary
from typing import List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from core.network_scanner import AccessPoint, Client
from utils.helpers import format_signal_strength

console = Console()


def show_main_menu() -> str:
    """Show main menu and get user choice"""
    choices = [
        "🎯 Saldırıya Başla",
        "❓ Yardım ve Kullanım Kılavuzu",
        "⚙️  Ayarlar",
        "🚪 Çıkış"
    ]
    
    choice = questionary.select(
        "Ana Menü:",
        choices=choices,
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan'),
        ])
    ).ask()
    
    if choice == choices[0]:
        return "attack"
    elif choice == choices[1]:
        return "help"
    elif choice == choices[2]:
        return "settings"
    else:
        return "exit"


def select_network(aps: List[AccessPoint], current_network: Optional[str] = None) -> Optional[AccessPoint]:
    """Show network selection menu"""
    if not aps:
        console.print("[red]✗ Ağ bulunamadı![/red]")
        return None
    
    # Create table
    table = Table(title="📡 Erişilebilir Ağlar", show_header=True, header_style="bold cyan")
    table.add_column("#", style="cyan", width=4)
    table.add_column("SSID", style="white", width=25)
    table.add_column("BSSID", style="dim white", width=20)
    table.add_column("Kanal", style="yellow", width=8)
    table.add_column("Sinyal", style="green", width=25)
    table.add_column("Şifreleme", style="magenta", width=15)
    table.add_column("Cihaz", style="blue", width=8)
    
    # Add rows
    choices = []
    for idx, ap in enumerate(aps):
        # Check if this is current network
        is_current = current_network and ap.essid == current_network
        prefix = "📶 " if is_current else "   "
        suffix = " (Bağlı)" if is_current else ""
        
        display_name = f"{prefix}{ap.essid}{suffix}"
        
        table.add_row(
            str(idx),
            display_name,
            ap.bssid,
            str(ap.channel),
            format_signal_strength(ap.power),
            ap.encryption,
            str(len(ap.clients))
        )
        
        choices.append(f"[{idx}] {display_name}")
    
    console.print(table)
    console.print()
    
    # Get user selection
    choice = questionary.select(
        "Hedef ağı seçin (↑↓ ok tuşları):",
        choices=choices,
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan'),
        ])
    ).ask()
    
    if choice:
        # Extract index from choice
        idx = int(choice.split(']')[0].strip('['))
        return aps[idx]
    
    return None


def select_clients(clients: List[Client], user_mac: Optional[str] = None) -> Tuple[List[str], bool]:
    """Show client selection menu with checkboxes"""
    if not clients:
        console.print("[red]✗ Bağlı cihaz bulunamadı![/red]")
        return [], False
    
    # Create table
    table = Table(title="📱 Bağlı Cihazlar", show_header=True, header_style="bold cyan")
    table.add_column("MAC Adresi", style="white", width=20)
    table.add_column("Sinyal", style="green", width=15)
    table.add_column("Paket", style="yellow", width=10)
    table.add_column("Durum", style="magenta", width=20)
    
    # Add rows
    choices = []
    for client in clients:
        is_user = user_mac and client.mac.upper() == user_mac.upper()
        
        if is_user:
            status = "🖥️  Senin Cihazın"
            style = "bold green"
            table.add_row(
                client.mac,
                f"{client.power} dBm",
                str(client.packets),
                status,
                style=style
            )
        else:
            status = "📱 Hedef"
            table.add_row(
                client.mac,
                f"{client.power} dBm",
                str(client.packets),
                status
            )
            choices.append(client.mac)
    
    console.print(table)
    console.print()
    
    if not choices:
        console.print("[yellow]⚠️  Hedef alınabilecek cihaz yok (sadece senin cihazın var)[/yellow]")
        return [], False
    
    # Add "Select All" option
    choices.append("⚡ HEPSINE SALDIRI YAP")
    
    # Get user selection
    console.print("[cyan]Hedef cihazları seçin (Space: işaretle, Enter: devam):[/cyan]")
    selected = questionary.checkbox(
        "",
        choices=choices,
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan'),
        ])
    ).ask()
    
    if not selected:
        return [], False
    
    # Check if "Select All" was chosen
    if "⚡ HEPSINE SALDIRI YAP" in selected:
        return [c for c in choices if c != "⚡ HEPSINE SALDIRI YAP"], True
    
    return selected, False


def confirm_attack(target_count: int, ap_name: str) -> bool:
    """Confirm attack start"""
    console.print()
    console.print(f"[yellow]⚠️  {target_count} cihaza '{ap_name}' ağında saldırı başlatılacak![/yellow]")
    console.print()
    
    return questionary.confirm(
        "Devam etmek istiyor musunuz?",
        default=False
    ).ask()


def show_help():
    """Display help information"""
    help_text = """
[bold cyan]═══ KYKSKN KULLANIM KILAVUZU ═══[/bold cyan]

[bold white]Genel Bilgi:[/bold white]
KYKSKN, kablosuz ağlarda çoklu hedef deauthentication saldırıları gerçekleştiren
bir güvenlik test aracıdır. Kali Linux platformunda çalışır.

[bold white]Kullanım Adımları:[/bold white]
1. Programı root yetkisiyle çalıştırın
2. Ana menüden "Saldırıya Başla"yı seçin
3. Hedef ağı seçin
4. Saldırı yapılacak cihazları seçin (kendi cihazınız otomatik hariç tutulur)
5. Saldırıyı başlatın ve dashboard'dan takip edin

[bold white]Özellikler:[/bold white]
• Otomatik wireless adapter tespiti
• Monitor mode yönetimi
• Gerçek zamanlı ağ tarama
• Çoklu hedef desteği
• Cihaz hariç tutma (whitelist)
• Canlı saldırı istatistikleri
• Detaylı loglama

[bold white]Kısayollar:[/bold white]
• Ctrl+C: Saldırıyı durdur
• ↑↓: Menüde gezin
• Space: Seçim yap
• Enter: Onayla

[bold white]Gereksinimler:[/bold white]
• Kali Linux (2020.1+)
• Python 3.8+
• Root yetkisi
• Monitor mode destekleyen wireless adapter

[bold white]Yasal Uyarı:[/bold white]
Bu araç sadece eğitim ve yasal güvenlik testleri için kullanılmalıdır.
İzinsiz kullanım yasadışıdır.

[bold white]Destek:[/bold white]
GitHub: github.com/kykskn
"""
    
    console.print(help_text)
    
    questionary.press_any_key_to_continue("Devam etmek için bir tuşa basın...").ask()


def show_settings():
    """Display settings menu"""
    console.print("[yellow]⚙️  Ayarlar menüsü henüz geliştiriliyor...[/yellow]")
    questionary.press_any_key_to_continue("Devam etmek için bir tuşa basın...").ask()

