# modules/discord_tools.py
import requests
import random
import string
import time
import logging
import json
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def save_result(data: dict, token_type: str):
    try:
        filename = f"token_{token_type}_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Résultat sauvegardé → {filename}")
    except Exception as e:
        logging.error(f"Erreur sauvegarde : {e}")


def advanced_2fa_check(headers: dict, console: Console) -> dict:
    twofa_info = {
        "mfa_enabled": False,
        "level": "Aucun",
        "method": "Inconnu",
        "backup_codes": False,
        "phone_verified": False
    }
    try:
        r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=8)
        if r.status_code == 200:
            data = r.json()
            twofa_info["mfa_enabled"] = data.get("mfa_enabled", False)

        r = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=headers, timeout=8)
        if r.status_code == 200:
            twofa_info["level"] = "Élevé"
            twofa_info["method"] = "Discord Authenticator + SMS"
        elif r.status_code == 403:
            twofa_info["level"] = "Moyen"

        try:
            bc = requests.get("https://discord.com/api/v9/users/@me/backup-codes", headers=headers, timeout=6)
            twofa_info["backup_codes"] = bc.status_code == 200
        except:
            pass
    except:
        pass
    return twofa_info


def check_token(token: str, console: Console):
    console.status("[cyan]Analyse complète du token (User/Bot + 2FA Avancée)...[/cyan]", spinner="dots").start()
    
    token = token.strip()
    if len(token) < 50:
        console.print("[red]❌ Token trop court ou invalide[/red]")
        return

    headers = {**HEADERS_BASE, "Authorization": token}
    r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=10)

    if r.status_code == 401:
        headers["Authorization"] = f"Bot {token}"
        r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=10)
        token_type = "BOT"
    else:
        token_type = "USER"

    if r.status_code != 200:
        console.print(f"[red]❌ Token invalide ou révoqué (HTTP {r.status_code})[/red]")
        return

    data = r.json()
    twofa = advanced_2fa_check(headers, console)

    table = Table(title=f"✅ TOKEN {token_type} VALIDE - ANALYSE COMPLÈTE", style="green")
    table.add_column("Information", style="cyan")
    table.add_column("Résultat")

    table.add_row("Type", f"[bold]{token_type}[/bold]")
    table.add_row("Username", f"{data.get('username')}#{data.get('discriminator')}")
    table.add_row("User ID", data.get("id"))
    table.add_row("Email", data.get("email", "[Masqué]"))
    table.add_row("Téléphone", data.get("phone", "Non lié"))
    table.add_row("Nitro", "Oui" if data.get("premium_type", 0) > 0 else "Non")
    table.add_row("2FA Basique", "[green]Activé[/green]" if twofa["mfa_enabled"] else "[red]Désactivé[/red]")
    table.add_row("Niveau 2FA", twofa["level"])
    table.add_row("Méthode", twofa["method"])
    table.add_row("Codes de secours", "[green]Oui[/green]" if twofa["backup_codes"] else "[red]Non[/red]")

    if data.get("id"):
        created = (int(data["id"]) >> 22) + 1420070400000
        table.add_row("Compte créé", datetime.fromtimestamp(created/1000).strftime("%d/%m/%Y %H:%M"))

    console.print(table)

    if twofa["mfa_enabled"]:
        console.print(Panel("[green]Compte protégé par 2FA[/green]", border_style="green"))
    else:
        console.print(Panel("[red]Ce compte n'a PAS de 2FA → Vulnérable[/red]", border_style="red"))

    save_result({**data, "2fa_advanced": twofa}, token_type.lower())


def webhook_spammer(console: Console, config: dict):
    url = Prompt.ask("[cyan]Webhook URL[/cyan]")
    msg = Prompt.ask("[cyan]Message[/cyan]")
    count = int(Prompt.ask("[cyan]Nombre d'envois[/cyan]", default=str(config.get("max_webhook_spam", 50))))
    delay = float(Prompt.ask("[cyan]Delay (s)[/cyan]", default="1.0"))
    sent = 0
    for i in range(count):
        try:
            requests.post(url, json={"content": msg}, timeout=8)
            sent += 1
        except:
            pass
        time.sleep(delay)
    console.print(f"[green]Spam terminé → {sent}/{count} messages[/green]")


def webhook_info_and_delete(console: Console):
    url = Prompt.ask("[cyan]Webhook URL[/cyan]")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            table = Table(title="Webhook Info")
            table.add_column("Info"); table.add_column("Valeur")
            table.add_row("Nom", data.get("name"))
            table.add_row("ID", data.get("id"))
            console.print(table)

            if Prompt.ask("Supprimer ce webhook ?", choices=["y","n"], default="n") == "y":
                dr = requests.delete(url)
                console.print("[green]Webhook supprimé[/green]" if dr.status_code in (200,204) else "[red]Échec[/red]")
    except Exception as e:
        console.print(f"[red]Erreur : {e}[/red]")


def generate_fake_token(console: Console):
    console.print("[yellow]Génération de tokens fictifs...[/yellow]")
    for _ in range(5):
        fake = "mfa." + ''.join(random.choices(string.ascii_letters + string.digits + "-_", k=80))
        console.print(f"[magenta]{fake}[/magenta]")


# ====================== MENU DISCORD ======================
def discord_menu(console: Console, config: dict):
    while True:
        console.clear()
        console.print(Panel("[bold magenta]MODULE DISCORD v1.4[/bold magenta]", border_style="magenta"))
        console.print("1. Token Checker (User/Bot + 2FA Avancée)")
        console.print("2. Webhook Spammer")
        console.print("3. Webhook Info + Delete")
        console.print("4. Fake Token Generator")
        console.print("5. Nitro Generator")
        console.print("0. Retour\n")

        choice = Prompt.ask("[bold yellow]Votre choix[/bold yellow]", choices=["0","1","2","3","4","5"], default="0")

        if choice == "0":
            break
        elif choice == "1":
            token = Prompt.ask("Colle ton token Discord", password=True)
            check_token(token, console)
        elif choice == "2":
            webhook_spammer(console, config)
        elif choice == "3":
            webhook_info_and_delete(console)
        elif choice == "4":
            generate_fake_token(console)
        elif choice == "5":
            cnt = int(Prompt.ask("Nombre de codes Nitro", default="15"))
            for _ in range(cnt):
                code = ''.join(random.choices(string.ascii_letters + string.digits, k=19))
                console.print(f"[bright_magenta]https://discord.gift/{code}[/bright_magenta]")

        input("\n[bold]Appuyez sur Entrée pour continuer...[/bold]")