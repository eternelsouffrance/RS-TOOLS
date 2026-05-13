# assets/banner.py
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import os
import time
import json

console = Console()

def get_nickname():
    """Récupère le surnom depuis config.json"""
    try:
        if os.path.exists("config.json"):
            with open("config.json", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("nickname", "Utilisateur")
    except:
        pass
    try:
        return os.getlogin()
    except:
        return "Hacker"

def print_banner():
    nickname = get_nickname()

    banner = Text("""
    ██████╗ ███████╗    ████████╗ ██████╗  ██████╗ ██╗     ███████╗
    ██╔══██╗██╔════╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
    ██████╔╝███████╗       ██║   ██║   ██║██║   ██║██║     ███████╗
    ██╔══██╗╚════██║       ██║   ██║   ██║██║   ██║██║     ╚════██║
    ██║  ██║███████║       ██║   ╚██████╔╝╚██████╔╝███████╗███████║
    ╚═╝  ╚═╝╚══════╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
    """, style="bold red")

    console.print(Panel(banner, 
                        title="RS TOOLS v1.5",
                        subtitle="Aucune limite. Aucun bug. Aucune échappatoire.",
                        border_style="bright_blue"))

    greeting = f"Bonjour [bold cyan]@{nickname}[/bold cyan], qu’est-ce qu’on fait aujourd’hui ? 🔥"
    console.print(Panel(greeting, 
                        title="👋 Bienvenue",
                        border_style="magenta",
                        padding=(1, 4)))

    console.print("[bold yellow]Développé par No Escape • Multi-tool Cybersécurité & OSINT[/bold yellow]\n")
    time.sleep(0.6)