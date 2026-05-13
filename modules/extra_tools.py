# modules/extra_tools.py
import os
import json
import glob
import shutil
import random
import string
import logging
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

console = Console()

# ====================== FONCTIONS UTILITAIRES ======================
def list_saved_results(console: Console):
    console.status("[cyan]Recherche des résultats sauvegardés...[/cyan]", spinner="dots").start()
    files = glob.glob("*.json") + glob.glob("network_*.json") + glob.glob("osint_*.json") + glob.glob("token_*.json")
    
    if not files:
        console.print("[yellow]Aucun résultat sauvegardé pour le moment.[/yellow]")
        return

    table = Table(title="📁 Résultats Sauvegardés", style="cyan")
    table.add_column("Fichier"); table.add_column("Date"); table.add_column("Taille (Ko)")
    
    for f in sorted(files, reverse=True):
        size = os.path.getsize(f) / 1024
        date = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%d/%m/%Y %H:%M")
        table.add_row(f, date, f"{size:.2f}")
    
    console.print(table)

def view_result_file(console: Console):
    files = glob.glob("*.json")
    if not files:
        console.print("[red]Aucun fichier trouvé.[/red]")
        return
    file_name = Prompt.ask("Nom du fichier à lire", choices=[f for f in files] + ["annuler"])
    if file_name == "annuler": return
    try:
        with open(file_name, encoding="utf-8") as f:
            data = json.load(f)
        console.print(Panel(json.dumps(data, indent=2, ensure_ascii=False), title=f"Contenu de {file_name}", border_style="green"))
    except Exception as e:
        console.print(f"[red]Erreur lecture : {e}[/red]")

def generate_strong_password(console: Console):
    length = int(Prompt.ask("Longueur du mot de passe", default="20"))
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    pwd = ''.join(random.choice(chars) for _ in range(length))
    console.print(Panel(f"[bold green]{pwd}[/bold green]", title="🔑 Mot de Passe Généré", border_style="green"))
    console.print("[yellow]Conseil : Utilise un gestionnaire de mots de passe ![/yellow]")

def fake_identity(console: Console):
    identities = [
        {"Nom": "Jean Dupont", "Email": "jean.dupont92@gmail.com", "Téléphone": "+33612345678", "IP": "185.45.67.89"},
        {"Nom": "Sophie Laurent", "Email": "sophie.l92@proton.me", "Téléphone": "+33798765432", "IP": "91.234.56.12"},
        {"Nom": "Lucas Moreau", "Email": "lucas.moreau@outlook.fr", "Téléphone": "+33698765432", "IP": "176.23.45.67"}
    ]
    identity = random.choice(identities)
    table = Table(title="🕵️ Identité Fictive")
    table.add_column("Champ"); table.add_column("Valeur")
    for k, v in identity.items():
        table.add_row(k, v)
    console.print(table)

def view_logs(console: Console):
    logs = glob.glob("logs/*.log")
    if not logs:
        console.print("[yellow]Aucun log trouvé.[/yellow]")
        return
    latest = max(logs, key=os.path.getmtime)
    with open(latest, encoding="utf-8") as f:
        content = f.read()[-1500:]  # Dernières 1500 lignes
    console.print(Panel(content, title=f"📜 Dernier log : {os.path.basename(latest)}", border_style="yellow"))

def clear_temp_files(console: Console):
    try:
        count = 0
        for ext in ["*.json", "*.log", "*.tmp"]:
            for f in glob.glob(ext):
                if "rs_tools" not in f.lower():
                    os.remove(f)
                    count += 1
        console.print(f"[green]✅ {count} fichiers temporaires supprimés.[/green]")
    except Exception as e:
        console.print(f"[red]{e}[/red]")

def edit_config(console: Console):
    if not os.path.exists("config.json"):
        console.print("[red]config.json non trouvé.[/red]")
        return
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
    
    console.print(Panel(str(config), title="Configuration Actuelle"))
    key = Prompt.ask("Clé à modifier (ou 'exit')")
    if key == "exit": return
    value = Prompt.ask(f"Nouvelle valeur pour {key}")
    try:
        config[key] = int(value) if value.isdigit() else float(value) if "." in value else value
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        console.print("[green]Configuration mise à jour ![/green]")
    except:
        console.print("[red]Erreur lors de la modification.[/red]")

# ====================== MENU EXTRA TOOLS ======================
def extra_menu(console: Console):
    while True:
        console.clear()
        console.print(Panel("[bold magenta]EXTRA TOOLS v1.5[/bold magenta]", border_style="magenta"))
        console.print("1. Lister tous les résultats sauvegardés")
        console.print("2. Lire un fichier résultat")
        console.print("3. Générateur de mot de passe fort")
        console.print("4. Générateur d'identité fictive")
        console.print("5. Visionner les logs")
        console.print("6. Éditer la configuration")
        console.print("7. Nettoyer fichiers temporaires")
        console.print("8. À propos de RS TOOLS")
        console.print("0. Retour au menu principal\n")

        choice = Prompt.ask("[bold yellow]Votre choix[/bold yellow]", choices=["0","1","2","3","4","5","6","7","8"])

        if choice == "0": break
        elif choice == "1": list_saved_results(console)
        elif choice == "2": view_result_file(console)
        elif choice == "3": generate_strong_password(console)
        elif choice == "4": fake_identity(console)
        elif choice == "5": view_logs(console)
        elif choice == "6": edit_config(console)
        elif choice == "7": clear_temp_files(console)
        elif choice == "8":
            console.print(Panel(
                "RS TOOLS v1.5\n"
                "Développé par No Escape\n"
                "Outil multi-fonctions Cybersécurité & OSINT\n\n"
                "• Architecture modulaire\n"
                "• Sauvegarde automatique des résultats\n"
                "• Compatible Windows & Linux\n"
                "• Zéro API payante\n\n"
                "[bold]Aucune limite. Aucun bug. Aucune échappatoire.[/bold]",
                title="ℹ️  À Propos", border_style="bright_green"
            ))

        input("\n[bold]Appuyez sur Entrée pour continuer...[/bold]")