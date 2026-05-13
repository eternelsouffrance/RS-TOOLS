# modules/osint_tools.py
import socket
import whois
import dns.resolver
import requests
import re
import json
import logging
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

# ====================== FONCTIONS COMMUNES ======================
def save_osint_result(data: dict, tool_name: str):
    try:
        filename = f"osint_{tool_name}_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Résultat OSINT sauvegardé → {filename}")
        return filename
    except Exception as e:
        logging.error(f"Erreur sauvegarde : {e}")
        return None


# ====================== IP LOOKUP AVANCÉ ======================
def ip_lookup(ip: str, console: Console):
    console.status(f"[cyan]Analyse avancée de l'IP {ip}...[/cyan]", spinner="dots").start()
    result = {"ip": ip}

    try:
        # Hostname
        try:
            result["hostname"] = socket.gethostbyaddr(ip)[0]
        except:
            result["hostname"] = "N/A"

        # WHOIS
        w = whois.whois(ip)
        result.update({
            "isp": w.org or w.netname or "N/A",
            "country": w.country or "N/A",
            "city": getattr(w, "city", "N/A"),
            "asn": getattr(w, "asn", "N/A"),
            "created": str(w.creation_date)[:19] if w.creation_date else "N/A"
        })

        table = Table(title=f"🛰️ IP LOOKUP → {ip}", style="bright_blue")
        table.add_column("Information", style="cyan")
        table.add_column("Résultat")
        for k, v in result.items():
            table.add_row(k.capitalize(), str(v))
        
        console.print(table)
        save_osint_result(result, "ip_lookup")

    except Exception as e:
        console.print(f"[red]Erreur IP Lookup : {e}[/red]")


# ====================== USERNAME TRACKER ÉTENDU ======================
def username_tracker(username: str, console: Console):
    console.status(f"[cyan]Traque du pseudo @{username} sur 12 plateformes...[/cyan]", spinner="dots").start()

    sites = {
        "GitHub": f"https://github.com/{username}",
        "Twitter/X": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "GitLab": f"https://gitlab.com/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "Discord": f"https://discord.com/users/{username}"  # simulation
    }

    table = Table(title=f"🔍 Username Tracker → @{username}", style="magenta")
    table.add_column("Plateforme"); table.add_column("Statut"); table.add_column("Lien")

    found_on = []
    with Progress() as progress:
        task = progress.add_task("[green]Scanning...", total=len(sites))
        for name, url in sites.items():
            try:
                r = requests.get(url, timeout=7, allow_redirects=True)
                status = "[green]✅ Existant[/green]" if r.status_code == 200 and "not found" not in r.text.lower()[:800] else "[red]❌ Non trouvé[/red]"
                if "Existant" in status:
                    found_on.append(name)
            except:
                status = "[yellow]⚠️ Erreur[/yellow]"
            table.add_row(name, status, url[:60] + "..." if len(url) > 60 else url)
            progress.update(task, advance=1)

    console.print(table)
    console.print(f"[green]Trouvé sur {len(found_on)} plateformes : {', '.join(found_on) if found_on else 'Aucune'}[/green]")
    save_osint_result({"username": username, "found_on": found_on}, "username_tracker")


# ====================== EMAIL OSINT AVANCÉ ======================
def email_osint(email: str, console: Console):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        console.print("[red]Format email invalide[/red]")
        return

    domain = email.split("@")[1]
    console.status(f"[cyan]Analyse approfondie de {email}...[/cyan]", spinner="dots").start()

    result = {"email": email, "domain": domain}

    # MX Records
    try:
        mx = [str(x) for x in dns.resolver.resolve(domain, "MX")]
        result["mx"] = mx
    except:
        result["mx"] = ["N/A"]

    # WHOIS Domaine
    try:
        w = whois.whois(domain)
        result["domain_created"] = str(w.creation_date)[:19] if w.creation_date else "N/A"
        result["registrar"] = w.registrar or "N/A"
    except:
        result["domain_created"] = "N/A"

    table = Table(title="📧 EMAIL OSINT", style="cyan")
    table.add_column("Info"); table.add_column("Valeur")
    for k, v in result.items():
        table.add_row(k.replace("_", " ").capitalize(), str(v)[:100])

    console.print(table)
    save_osint_result(result, "email_osint")


# ====================== PHONE OSINT ======================
def phone_osint(phone: str, console: Console):
    console.status(f"[cyan]Analyse du numéro {phone}...[/cyan]", spinner="dots").start()
    
    # Nettoyage
    clean = re.sub(r"\D", "", phone)
    result = {
        "phone": phone,
        "clean": f"+{clean}" if not clean.startswith("00") else clean,
        "country": "France / Europe" if clean.startswith("33") else "International",
        "carrier": "Orange / SFR / Free / Bouygues (simulation)",
        "type": "Mobile" if len(clean) > 9 else "Fixe / Inconnu",
        "valid": len(clean) >= 10
    }

    table = Table(title="📱 PHONE OSINT", style="yellow")
    table.add_column("Information"); table.add_column("Résultat")
    for k, v in result.items():
        table.add_row(k.capitalize(), str(v))
    
    console.print(table)
    save_osint_result(result, "phone_osint")


# ====================== DOMAIN OSINT (NOUVEAU) ======================
def domain_osint(domain: str, console: Console):
    console.status(f"[cyan]Analyse du domaine {domain}...[/cyan]", spinner="dots").start()
    # (Même logique que email mais centré domaine)
    console.print(Panel(f"Domain OSINT pour [bold]{domain}[/bold] - Informations WHOIS + DNS", border_style="green"))
    # Tu peux étendre ici


# ====================== MENU OSINT ======================
def osint_menu(console: Console):
    while True:
        console.clear()
        console.print(Panel("[bold cyan]MODULE OSINT v1.3 - Advanced Recon[/bold cyan]", border_style="cyan"))
        console.print("1. IP Lookup (Géo + ASN)")
        console.print("2. Username Tracker (12 plateformes)")
        console.print("3. Email OSINT Complet")
        console.print("4. Phone Number Analyzer")
        console.print("5. Domain OSINT")
        console.print("0. Retour au menu principal\n")

        choice = Prompt.ask("[bold yellow]Votre choix[/bold yellow]", choices=["0","1","2","3","4","5"], default="0")

        if choice == "0":
            break
        elif choice == "1":
            ip = Prompt.ask("Adresse IP à analyser")
            ip_lookup(ip, console)
        elif choice == "2":
            user = Prompt.ask("Pseudo à traquer (sans @)")
            username_tracker(user, console)
        elif choice == "3":
            email = Prompt.ask("Adresse email")
            email_osint(email, console)
        elif choice == "4":
            phone = Prompt.ask("Numéro de téléphone (+33 ou international)")
            phone_osint(phone, console)
        elif choice == "5":
            domain = Prompt.ask("Domaine (ex: example.com)")
            domain_osint(domain, console)

        input("\n[bold]Appuyez sur Entrée pour continuer...[/bold]")