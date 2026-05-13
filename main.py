# main.py
import os
import json
import logging
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from assets.banner import print_banner
from modules.discord_tools import discord_menu
from modules.osint_tools import osint_menu
from modules.network_tools import network_menu
from modules.system_tools import system_menu
from modules.extra_tools import extra_menu

console = Console()

def load_config():
    config_path = "config.json"
    default_config = {
        "max_webhook_spam": 50,
        "default_delay": 1.0,
        "theme": "dark",
        "nickname": "Utilisateur"
    }
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_config

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/rs_tools_{datetime.now():%Y-%m-%d}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
        force=True
    )

def main_menu():
    config = load_config()
    while True:
        console.clear()
        print_banner()

        console.print(Panel("[bold cyan]MENU PRINCIPAL RS TOOLS v1.5[/bold cyan]", border_style="bright_blue"))
        console.print("[1]  Discord Tools")
        console.print("[2]  OSINT Tools")
        console.print("[3]  Network Tools")
        console.print("[4]  System Tools")
        console.print("[5]  Extra Tools")
        console.print("[0]  Quitter\n")

        choice = Prompt.ask("[bold yellow]Votre choix[/bold yellow]", choices=["0","1","2","3","4","5"], default="0")

        if choice == "0":
            console.print("[bold red]Fermeture de RS TOOLS...[/bold red]")
            logging.info("Session terminée")
            break
        elif choice == "1": discord_menu(console, config)
        elif choice == "2": osint_menu(console)
        elif choice == "3": network_menu(console)
        elif choice == "4": system_menu(console)
        elif choice == "5": extra_menu(console)

if __name__ == "__main__":
    setup_logger()
    logging.info("=== RS TOOLS v1.5 démarré ===")
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrompu par l'utilisateur.[/bold red]")
    except Exception as e:
        logging.exception("Erreur critique")
        console.print(f"[bold red]Erreur critique : {e}[/bold red]")
    finally:
        console.print("[bold green]À bientôt dans la matrice.[/bold green]")