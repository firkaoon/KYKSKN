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
    """Display KYKSKN banner with enhanced visuals"""
    # Generate ASCII art with gradient effect
    ascii_art = pyfiglet.figlet_format(APP_NAME, font='slant')
    
    # Create colored text with effects
    banner_text = Text()
    
    # ASCII art with gradient effect (cyan to blue)
    lines = ascii_art.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            # Gradient effect: cyan -> bright_cyan -> blue
            if i < len(lines) // 3:
                style = "bold cyan"
            elif i < len(lines) * 2 // 3:
                style = "bold bright_cyan"
            else:
                style = "bold blue"
            banner_text.append(line + "\n", style=style)
    
    # Version info with sparkle effect
    banner_text.append(f"\nVersion {APP_VERSION} - 2025", style="dim white")
    banner_text.append(" ✨", style="bold yellow")
    banner_text.append("\n", style="")
    
    # Created by with animated effect
    creator_text = Text()
    creator_text.append("┌─", style="bold cyan")
    creator_text.append(" Created by ", style="bold white")
    creator_text.append("Firkaoon ", style="bold bright_magenta blink")
    creator_text.append("─┐", style="bold cyan")
    
    banner_text.append("\n")
    banner_text.append(creator_text)
    banner_text.append("\n")
    
    # Display in enhanced panel
    panel = Panel(
        banner_text,
        border_style="bright_cyan",
        box="double",
        padding=(1, 2),
        title="[bold bright_cyan]⚡ KYKSKN ⚡[/bold bright_cyan]",
        title_align="center"
    )
    
    console.print(panel)


def show_legal_warning():
    """Display legal warning with enhanced visuals"""
    warning_text = Text()
    warning_text.append("⚠️  ", style="bold yellow")
    warning_text.append("YASAL UYARI", style="bold bright_yellow blink")
    warning_text.append("  ⚠️\n\n", style="bold yellow")
    warning_text.append("Bu araç SADECE:\n", style="bold white")
    warning_text.append("  • ", style="dim white")
    warning_text.append("Kendi ağınızda test amaçlı\n", style="green")
    warning_text.append("  • ", style="dim white")
    warning_text.append("İzin alınmış ağlarda güvenlik denetimi için\n", style="green")
    warning_text.append("  • ", style="dim white")
    warning_text.append("Eğitim amaçlı kullanılmalıdır.\n\n", style="green")
    warning_text.append("⚠️  ", style="bold red")
    warning_text.append("İzinsiz kullanım YASADIDIR ve ciddi yasal sonuçları vardır.\n", style="bold red")
    warning_text.append("Devam ederek bu şartları kabul etmiş sayılırsınız.\n", style="dim white")
    
    panel = Panel(
        warning_text,
        title="[bold bright_red]⚠️  UYARI  ⚠️[/bold bright_red]",
        border_style="bright_red",
        box="double",
        padding=(1, 2)
    )
    
    console.print(panel)


def show_section_header(title: str, subtitle: str = ""):
    """Display section header with enhanced visuals"""
    text = Text()
    text.append("╔═══ ", style="bold bright_cyan")
    text.append(title, style="bold white")
    text.append(" ═══╗\n", style="bold bright_cyan")
    if subtitle:
        text.append("║ ", style="dim cyan")
        text.append(subtitle, style="dim white")
        text.append(" ║\n", style="dim cyan")
        text.append("╚", style="dim cyan")
        text.append("═" * (len(title) + 8), style="dim cyan")
        text.append("╝", style="dim cyan")
    
    console.print()
    console.print(text)
    console.print()


def show_success(message: str):
    """Display success message with enhanced visuals"""
    text = Text()
    text.append("✓ ", style="bold green")
    text.append(message, style="green")
    console.print(text)


def show_error(message: str):
    """Display error message with enhanced visuals"""
    text = Text()
    text.append("✗ ", style="bold red")
    text.append(message, style="red")
    console.print(text)


def show_warning(message: str):
    """Display warning message with enhanced visuals"""
    text = Text()
    text.append("⚠️  ", style="bold yellow")
    text.append(message, style="yellow")
    console.print(text)


def show_info(message: str):
    """Display info message with enhanced visuals"""
    text = Text()
    text.append("ℹ️  ", style="bold blue")
    text.append(message, style="blue")
    console.print(text)


def show_loading(message: str):
    """Display loading message with enhanced visuals"""
    text = Text()
    text.append("⚙️  ", style="bold yellow")
    text.append(message, style="yellow")
    console.print(text)

