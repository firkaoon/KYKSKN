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
    """Display KYKSKN banner with enhanced visual effects"""
    # Generate ASCII art
    ascii_art = pyfiglet.figlet_format(APP_NAME, font='slant')
    
    # Create banner text
    banner_text = Text()
    
    # ASCII art with gradient effect - basit renkler kullan
    colors = ["bold cyan", "bold bright_cyan", "bold blue", "bold bright_blue", "bold magenta", "bold bright_magenta"]
    lines = ascii_art.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            color_index = (i // 2) % len(colors)
            # Direkt stil string kullan (f-string veya + kullanma)
            banner_text.append(line + '\n', style=colors[color_index])
    
    banner_text.append("\n", style="")
    
    # "Created by Firkaoon" with gradient
    creator_text = Text()
    creator_text.append("╔" + "═" * 48 + "╗\n", style="bright_cyan")
    creator_text.append("║", style="bright_cyan")
    creator_text.append(" " * 10, style="")
    
    creator_name = "Created by Firkaoon"
    # Direkt stil string'leri kullan (f-string veya + kullanma)
    gradient_styles = ["bold cyan", "bold bright_cyan", "bold blue", "bold bright_blue", 
                      "bold magenta", "bold bright_magenta", "bold yellow", "bold bright_yellow"]
    for idx, char in enumerate(creator_name):
        if char == ' ':
            creator_text.append(char, style="")
        else:
            style = gradient_styles[idx % len(gradient_styles)]
            creator_text.append(char, style=style)
    
    creator_text.append(" " * 10, style="")
    creator_text.append("║\n", style="bright_cyan")
    creator_text.append("╚" + "═" * 48 + "╝\n", style="bright_cyan")
    
    banner_text.append(creator_text)
    banner_text.append(f"\n{' ' * 15}Version {APP_VERSION} - 2025\n", style="dim white")
    
    # Panel oluştur - title'ı basit string yap (markdown sorun çıkarabilir)
    panel = Panel(
        banner_text,
        border_style="bright_cyan",
        box="double",
        padding=(2, 4),
        title="╔═══ KYKSKN ═══╗",
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
        title="UYARI",
        border_style="red",
        padding=(1, 2)
    )
    
    console.print(panel)


def show_section_header(title: str, subtitle: str = ""):
    """Display section header with enhanced visual effects"""
    # Create decorative header
    header_text = Text()
    header_length = len(title) + 8
    header_text.append("╔" + "═" * header_length + "╗\n", style="bright_cyan")
    header_text.append("║", style="bright_cyan")
    header_text.append(" " * 3, style="")
    header_text.append(f"✨ {title} ✨", style="bold bright_yellow")
    header_text.append(" " * 3, style="")
    header_text.append("║\n", style="bright_cyan")
    header_text.append("╚" + "═" * header_length + "╝\n", style="bright_cyan")
    
    if subtitle:
        header_text.append(f"\n{subtitle}\n", style="dim white")
    
    console.print()
    console.print(header_text)
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
    console.print(f"[bold blue]ℹ️[/bold blue]  [blue]{message}[/blue]")


def show_loading(message: str):
    """Display loading message with animated spinner"""
    console.print(f"[bold yellow]⚙️[/bold yellow]  [yellow]{message}[/yellow]")

