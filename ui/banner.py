"""
KYKSKN - Banner and ASCII Art
"""

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from config.settings import APP_NAME, APP_VERSION, APP_DESCRIPTION

console = Console()


def show_banner():
    """Display KYKSKN banner"""
    # Generate ASCII art
    ascii_art = pyfiglet.figlet_format(APP_NAME, font='slant')
    
    # Create colored text
    banner_text = Text()
    banner_text.append(ascii_art, style="bold cyan")
    banner_text.append(f"\n{APP_DESCRIPTION}\n", style="bold white")
    banner_text.append(f"Version {APP_VERSION} - 2025\n", style="dim white")
    
    # Display in panel
    panel = Panel(
        banner_text,
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(panel)


def show_legal_warning():
    """Display legal warning"""
    warning_text = Text()
    warning_text.append("⚠️  YASAL UYARI ⚠️\n\n", style="bold yellow")
    warning_text.append("Bu araç SADECE:\n", style="white")
    warning_text.append("  • Kendi ağınızda test amaçlı\n", style="green")
    warning_text.append("  • İzin alınmış ağlarda güvenlik denetimi için\n", style="green")
    warning_text.append("  • Eğitim amaçlı kullanılmalıdır.\n\n", style="green")
    warning_text.append("İzinsiz kullanım YASADIDIR ve ciddi yasal sonuçları vardır.\n", style="bold red")
    warning_text.append("Devam ederek bu şartları kabul etmiş sayılırsınız.\n", style="dim white")
    
    panel = Panel(
        warning_text,
        title="[bold red]UYARI[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    
    console.print(panel)


def show_section_header(title: str, subtitle: str = ""):
    """Display section header"""
    text = Text()
    text.append(f"═══ {title} ═══\n", style="bold cyan")
    if subtitle:
        text.append(subtitle, style="dim white")
    
    console.print()
    console.print(text)
    console.print()


def show_success(message: str):
    """Display success message"""
    console.print(f"[green]✓[/green] {message}")


def show_error(message: str):
    """Display error message"""
    console.print(f"[red]✗[/red] {message}")


def show_warning(message: str):
    """Display warning message"""
    console.print(f"[yellow]⚠️[/yellow]  {message}")


def show_info(message: str):
    """Display info message"""
    console.print(f"[blue]ℹ️[/blue]  {message}")


def show_loading(message: str):
    """Display loading message"""
    console.print(f"[yellow]⚙️[/yellow]  {message}")

