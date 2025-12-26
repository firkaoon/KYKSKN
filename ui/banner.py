"""
KYKSKN - Banner and ASCII Art
"""

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from config.settings import APP_NAME, APP_VERSION, APP_DESCRIPTION

console = Console()


def show_banner():
    """Display KYKSKN banner with enhanced visuals"""
    # Generate ASCII art with gradient effect
    ascii_art = pyfiglet.figlet_format(APP_NAME, font='slant')
    
    # Create colored text with effects
    banner_text = Text()
    
    # ASCII art with gradient effect (cyan to blue)
    lines = ascii_art.split('\n')
    colors = ['cyan', 'bright_cyan', 'blue', 'bright_blue', 'cyan']
    for i, line in enumerate(lines):
        if line.strip():
            color = colors[i % len(colors)]
            banner_text.append(line + '\n', style=f"bold {color}")
        else:
            banner_text.append('\n')
    
    # Add separator
    banner_text.append("─" * 60 + "\n", style="dim cyan")
    
    # Creator text with special effects
    creator_text = Text()
    creator_text.append("✨ ", style="bold yellow")
    creator_text.append(APP_DESCRIPTION, style="bold bright_magenta")
    creator_text.append(" ✨", style="bold yellow")
    
    # Add sparkle effect around creator name
    banner_text.append("\n")
    banner_text.append(creator_text)
    banner_text.append("\n")
    
    # Version info with subtle styling
    version_text = Text()
    version_text.append("Version ", style="dim white")
    version_text.append(APP_VERSION, style="bold cyan")
    version_text.append(" • ", style="dim white")
    version_text.append("2025", style="bold white")
    
    banner_text.append(version_text)
    banner_text.append("\n")
    
    # Display in enhanced panel with gradient border
    panel = Panel(
        Align.center(banner_text),
        border_style="bright_cyan",
        box="double",
        padding=(1, 3),
        title="[bold bright_cyan]⚡ KYKSKN ⚡[/bold bright_cyan]",
        title_align="center"
    )
    
    console.print()
    console.print(panel)
    console.print()


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
    text.append("╔", style="bold cyan")
    text.append("═" * (len(title) + 8), style="bold cyan")
    text.append("╗\n", style="bold cyan")
    text.append("║", style="bold cyan")
    text.append("   ", style="bold cyan")
    text.append(title, style="bold bright_cyan")
    text.append("   ", style="bold cyan")
    text.append("║\n", style="bold cyan")
    text.append("╚", style="bold cyan")
    text.append("═" * (len(title) + 8), style="bold cyan")
    text.append("╝", style="bold cyan")
    
    if subtitle:
        text.append("\n")
        text.append("  ", style="dim")
        text.append(subtitle, style="dim white italic")
    
    console.print()
    console.print(text)
    console.print()


def show_success(message: str):
    """Display success message with enhanced styling"""
    console.print(f"[bold green]✓[/bold green] [green]{message}[/green]")


def show_error(message: str):
    """Display error message with enhanced styling"""
    console.print(f"[bold red]✗[/bold red] [red]{message}[/red]")


def show_warning(message: str):
    """Display warning message with enhanced styling"""
    console.print(f"[bold yellow]⚠️[/bold yellow]  [yellow]{message}[/yellow]")


def show_info(message: str):
    """Display info message with enhanced styling"""
    console.print(f"[bold blue]ℹ️[/bold blue]  [cyan]{message}[/cyan]")


def show_loading(message: str):
    """Display loading message with spinner effect"""
    console.print(f"[bold yellow]⚙️[/bold yellow]  [yellow]{message}[/yellow]")

