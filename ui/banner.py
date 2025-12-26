"""
KYKSKN - Banner and ASCII Art
"""

import pyfiglet
import rich.box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from config.settings import APP_NAME, APP_VERSION, APP_DESCRIPTION

console = Console()


def show_banner():
    """Display KYKSKN banner with enhanced visuals"""
    # Generate ASCII art with gradient effect
    ascii_art = pyfiglet.figlet_format(APP_NAME, font='slant')
    
    # Create colored text with gradient effect
    banner_text = Text()
    
    # ASCII art with cyan gradient
    lines = ascii_art.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            # Gradient effect: darker to lighter
            intensity = min(255, 100 + (i * 10))
            banner_text.append(line + '\n', style=f"bold bright_cyan")
    
    # Creator text with special effects
    banner_text.append("\n", style="reset")
    banner_text.append("╔" + "═" * 48 + "╗\n", style="bold bright_cyan")
    banner_text.append("║", style="bold bright_cyan")
    banner_text.append(" " * 8, style="reset")
    banner_text.append("✨ ", style="bold bright_yellow")
    banner_text.append("Created by Firkaoon", style="bold bright_magenta")
    banner_text.append(" ✨", style="bold bright_yellow")
    banner_text.append(" " * 8, style="reset")
    banner_text.append("║\n", style="bold bright_cyan")
    banner_text.append("╚" + "═" * 48 + "╝\n", style="bold bright_cyan")
    
    banner_text.append(f"\nVersion {APP_VERSION} - 2025\n", style="dim white")
    
    # Display in enhanced panel
    panel = Panel(
        banner_text,
        border_style="bright_cyan",
        box=rich.box.ROUNDED,
        padding=(1, 3),
        title="[bold bright_cyan]⚡ KYKSKN ⚡[/bold bright_cyan]",
        title_align="center"
    )
    
    console.print(panel)
    console.print()  # Extra spacing


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
    """Display section header with enhanced visuals"""
    text = Text()
    text.append("╔" + "═" * (len(title) + 6) + "╗\n", style="bold bright_cyan")
    text.append("║", style="bold bright_cyan")
    text.append(f"  {title}  ", style="bold bright_yellow")
    text.append("║\n", style="bold bright_cyan")
    text.append("╚" + "═" * (len(title) + 6) + "╝\n", style="bold bright_cyan")
    if subtitle:
        text.append(f"  {subtitle}\n", style="dim white")
    
    console.print()
    console.print(text)
    console.print()


def show_success(message: str):
    """Display success message with enhanced style"""
    console.print(f"[bold green]✓[/bold green] [green]{message}[/green]")


def show_error(message: str):
    """Display error message with enhanced style"""
    console.print(f"[bold red]✗[/bold red] [red]{message}[/red]")


def show_warning(message: str):
    """Display warning message with enhanced style"""
    console.print(f"[bold yellow]⚠️[/bold yellow]  [yellow]{message}[/yellow]")


def show_info(message: str):
    """Display info message with enhanced style"""
    console.print(f"[bold blue]ℹ️[/bold blue]  [blue]{message}[/blue]")


def show_loading(message: str):
    """Display loading message with enhanced style"""
    console.print(f"[bold yellow]⚙️[/bold yellow]  [yellow]{message}[/yellow]")

