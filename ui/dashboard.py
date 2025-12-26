"""
KYKSKN - Live Attack Dashboard
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text

console = Console()


class AttackDashboard:
    """Live dashboard for monitoring attacks"""
    
    def __init__(self, ap_name: str, ap_bssid: str, target_count: int):
        self.ap_name = ap_name
        self.ap_bssid = ap_bssid
        self.target_count = target_count
        self.start_time = datetime.now()
        self.is_running = False
        
    def create_header(self) -> Panel:
        """Create dashboard header with enhanced visuals"""
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        
        header_text = Text()
        header_text.append("╔═══ ", style="bold bright_cyan")
        header_text.append("🎯 SALDIRI DURUMU", style="bold white")
        header_text.append(" ═══╗\n", style="bold bright_cyan")
        header_text.append("║ ", style="bold bright_cyan")
        header_text.append("Hedef Ağ: ", style="white")
        header_text.append(f"{self.ap_name}", style="bold bright_yellow")
        header_text.append(" ║\n", style="bold bright_cyan")
        header_text.append("║ ", style="bold bright_cyan")
        header_text.append("BSSID: ", style="dim white")
        header_text.append(f"{self.ap_bssid}", style="dim white")
        header_text.append(" ║\n", style="bold bright_cyan")
        header_text.append("║ ", style="bold bright_cyan")
        header_text.append("Süre: ", style="white")
        header_text.append(f"{elapsed_str}", style="bold bright_green")
        header_text.append(" ║\n", style="bold bright_cyan")
        header_text.append("╚", style="bold bright_cyan")
        header_text.append("═" * 35, style="bold bright_cyan")
        header_text.append("╝", style="bold bright_cyan")
        
        return Panel(header_text, border_style="bright_cyan", box="double", padding=(1, 2))
    
    def create_stats_panel(self, stats: Dict) -> Panel:
        """Create statistics panel with enhanced visuals"""
        stats_text = Text()
        
        # Overall stats with icons
        stats_text.append("📊 ", style="bold white")
        stats_text.append("Genel İstatistikler\n\n", style="bold white")
        
        stats_text.append("🎯 ", style="bold cyan")
        stats_text.append("Toplam Hedef: ", style="white")
        stats_text.append(f"{stats.get('total_targets', 0)}\n", style="bold bright_cyan")
        
        stats_text.append("⚡ ", style="bold green")
        stats_text.append("Aktif Saldırı: ", style="white")
        stats_text.append(f"{stats.get('active_targets', 0)}\n", style="bold bright_green")
        
        stats_text.append("✅ ", style="bold yellow")
        stats_text.append("Başarılı: ", style="white")
        stats_text.append(f"{stats.get('successful_targets', 0)}\n", style="bold bright_yellow")
        
        stats_text.append("📦 ", style="bold magenta")
        stats_text.append("Toplam Paket: ", style="white")
        stats_text.append(f"{stats.get('total_packets', 0):,}\n", style="bold bright_magenta")
        
        return Panel(stats_text, title="[bold bright_green]📊 İstatistikler[/bold bright_green]", border_style="bright_green", box="double", padding=(1, 2))
    
    def create_targets_table(self, targets: List[Dict]) -> Table:
        """Create targets status table with enhanced visuals"""
        table = Table(
            show_header=True, 
            header_style="bold bright_cyan", 
            title="[bold bright_cyan]🎯 Hedef Durumları[/bold bright_cyan]",
            border_style="bright_cyan",
            box="double"
        )
        
        table.add_column("MAC Adresi", style="white", width=20)
        table.add_column("Durum", style="green", width=20)
        table.add_column("Paket", style="yellow", width=10)
        table.add_column("Süre", style="cyan", width=10)
        
        for target in targets[:15]:  # Show max 15 targets
            mac = target.get('client_mac', 'Unknown')
            packets = target.get('packets_sent', 0)
            elapsed = target.get('elapsed_time', 0)
            is_active = target.get('is_active', False)
            successful = target.get('successful', False)
            
            # Format elapsed time
            elapsed_str = str(timedelta(seconds=int(elapsed))).split('.')[0]
            
            # Determine status with enhanced visuals
            if successful:
                status = "✅ Bağlantı kesildi"
                status_style = "bold bright_green"
            elif is_active:
                status = "🔄 Saldırı devam ediyor"
                status_style = "bold bright_yellow"
            else:
                status = "⏸️  Beklemede"
                status_style = "dim white"
            
            table.add_row(
                mac,
                status,
                f"{packets:,}",
                elapsed_str,
                style=status_style if successful else None
            )
        
        if len(targets) > 15:
            table.add_row(
                "...",
                f"ve {len(targets) - 15} hedef daha",
                "...",
                "...",
                style="dim"
            )
        
        return table
    
    def create_controls_panel(self) -> Panel:
        """Create controls panel with enhanced visuals"""
        controls_text = Text()
        controls_text.append("⌨️  ", style="bold white")
        controls_text.append("Kontroller\n\n", style="bold white")
        controls_text.append("┌─ ", style="dim yellow")
        controls_text.append("Ctrl+C", style="bold bright_yellow")
        controls_text.append(" ─┐\n", style="dim yellow")
        controls_text.append("└─ ", style="dim yellow")
        controls_text.append("Saldırıyı Durdur", style="white")
        controls_text.append(" ─┘", style="dim yellow")
        
        return Panel(controls_text, border_style="bright_yellow", box="double", padding=(1, 2))
    
    def generate_layout(self, stats: Dict, targets: List[Dict]) -> Layout:
        """Generate complete dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=6),
            Layout(name="body"),
            Layout(name="footer", size=5)
        )
        
        layout["header"].update(self.create_header())
        
        # Body with stats and targets
        body_layout = Layout()
        body_layout.split_row(
            Layout(name="stats", ratio=1),
            Layout(name="targets", ratio=2)
        )
        
        body_layout["stats"].update(self.create_stats_panel(stats))
        body_layout["targets"].update(self.create_targets_table(targets))
        
        layout["body"].update(body_layout)
        layout["footer"].update(self.create_controls_panel())
        
        return layout
    
    def run(self, get_stats_func, get_targets_func):
        """Run live dashboard"""
        self.is_running = True
        
        try:
            with Live(self.generate_layout({}, []), refresh_per_second=2, console=console) as live:
                while self.is_running:
                    try:
                        # Get current stats
                        stats = get_stats_func()
                        targets = get_targets_func()
                        
                        # Update layout
                        live.update(self.generate_layout(stats, targets))
                        
                        # Check if attack is still running
                        if not stats.get('is_attacking', False):
                            break
                        
                        time.sleep(0.5)
                        
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        console.print(f"[red]Dashboard error: {e}[/red]")
                        time.sleep(1)
                        
        except Exception as e:
            console.print(f"[red]Dashboard failed: {e}[/red]")
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop dashboard"""
        self.is_running = False


def show_attack_summary(stats: Dict, targets: List[Dict]):
    """Show attack summary after completion with enhanced visuals"""
    console.print("\n")
    summary_header = Text()
    summary_header.append("╔═══ ", style="bold bright_cyan")
    summary_header.append("SALDIRI ÖZETİ", style="bold white")
    summary_header.append(" ═══╗", style="bold bright_cyan")
    console.print(summary_header)
    console.print()
    
    # Summary table with enhanced visuals
    table = Table(show_header=False, box="double", border_style="bright_cyan")
    table.add_column("Metric", style="bold white", width=25)
    table.add_column("Value", style="bold bright_cyan")
    
    table.add_row("🎯 Toplam Hedef", str(stats.get('total_targets', 0)))
    table.add_row("✅ Başarılı Saldırı", str(stats.get('successful_targets', 0)))
    table.add_row("📦 Toplam Paket Gönderildi", f"{stats.get('total_packets', 0):,}")
    
    console.print(table)
    console.print()
    
    # Successful targets with enhanced visuals
    successful = [t for t in targets if t.get('successful', False)]
    if successful:
        success_text = Text()
        success_text.append("✅ ", style="bold bright_green")
        success_text.append("Başarılı Hedefler:", style="bold bright_green")
        console.print(success_text)
        for target in successful:
            console.print(f"  • [bold white]{target.get('client_mac', 'Unknown')}[/bold white] - [bold cyan]{target.get('packets_sent', 0):,}[/bold cyan] paket")
        console.print()
    
    # Failed targets with enhanced visuals
    failed = [t for t in targets if not t.get('successful', False)]
    if failed:
        failed_text = Text()
        failed_text.append("⚠️  ", style="bold bright_yellow")
        failed_text.append("Devam Eden/Başarısız Hedefler:", style="bold bright_yellow")
        console.print(failed_text)
        for target in failed:
            console.print(f"  • [bold white]{target.get('client_mac', 'Unknown')}[/bold white] - [bold cyan]{target.get('packets_sent', 0):,}[/bold cyan] paket")
        console.print()

