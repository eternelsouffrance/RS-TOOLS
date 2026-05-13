# modules/network_tools.py
import socket
import threading
import time
import re
import requests
import dns.resolver
import subprocess
import json
import logging
import ssl
from datetime import datetime
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

# ====================== SAVE RESULT ======================
def save_network_result(data: dict, tool_name: str):
    try:
        filename = f"network_{tool_name}_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Résultat sauvegardé → {filename}")
    except Exception as e:
        logging.error(f"Erreur sauvegarde : {e}")


# ====================== SSL CERTIFICATE ANALYZER (AMÉLIORÉ) ======================
def ssl_analyzer(target: str, console: Console):
    console.status(f"[cyan]Analyse SSL/TLS du certificat pour {target}...[/cyan]", spinner="dots").start()
    
    if not target.startswith(("http", "https")):
        target = "https://" + target
    hostname = target.split("//")[-1].split("/")[0].split(":")[0]
    port = 443

    result = {"target": hostname, "port": port}

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                # Extraction des données
                result.update({
                    "common_name": cert.get("subject", [[]])[0][0][1] if cert.get("subject") else "N/A",
                    "issuer": cert.get("issuer", [[]])[0][0][1] if cert.get("issuer") else "N/A",
                    "version": cert.get("version"),
                    "serial_number": cert.get("serialNumber"),
                    "not_before": cert.get("notBefore"),
                    "not_after": cert.get("notAfter"),
                    "san": cert.get("subjectAltName", []),
                    "fingerprint_sha256": cert.get("fingerprint", "N/A")
                })

                # Vérification expiration
                exp_date = datetime.strptime(cert.get("notAfter"), "%b %d %H:%M:%S %Y %Z")
                days_left = (exp_date - datetime.utcnow()).days
                result["days_remaining"] = days_left
                result["expired"] = days_left < 0

        # Table d'affichage
        table = Table(title=f"🔐 SSL/TLS Certificate Analysis → {hostname}", style="bright_green")
        table.add_column("Information", style="cyan")
        table.add_column("Valeur")

        table.add_row("Common Name", result["common_name"])
        table.add_row("Issuer", result["issuer"])
        table.add_row("Valid From", result["not_before"])
        table.add_row("Valid Until", result["not_after"])
        table.add_row("Jours restants", f"[{'green' if days_left > 30 else 'red'}]{days_left} jours[/]")
        table.add_row("Expired", "[red]OUI[/red]" if result["expired"] else "[green]Non[/green]")
        table.add_row("Subject Alt Names", "\n".join([f"• {san[1]}" for san in result["san"]]) or "Aucun")
        table.add_row("SHA256 Fingerprint", result["fingerprint_sha256"][:50] + "...")

        console.print(table)

        # Avertissements de sécurité
        if result["expired"]:
            console.print(Panel("[red]⚠️ CERTIFICAT EXPIRÉ ! Risque de sécurité élevé.[/red]", border_style="red"))
        elif days_left < 30:
            console.print(Panel(f"[yellow]⚠️ Certificat expire dans {days_left} jours.[/yellow]", border_style="yellow"))
        else:
            console.print(Panel("[green]✅ Certificat SSL valide et sécurisé.[/green]", border_style="green"))

        save_network_result(result, "ssl_analyzer")

    except ssl.SSLCertVerificationError:
        console.print("[red]❌ Certificat invalide ou auto-signé (erreur de vérification)[/red]")
    except Exception as e:
        console.print(f"[red]Erreur SSL Analyzer : {e}[/red]")


# ====================== AUTRES FONCTIONS (déjà améliorées précédemment) ======================
# (port_scanner, dns_lookup, website_scraper, ping_tool, wifi_scanner restent identiques à la version précédente)

# ====================== MENU NETWORK v1.5 ======================
def network_menu(console: Console):
    while True:
        console.clear()
        console.print(Panel("[bold green]MODULE NETWORK v1.5 - Advanced Recon[/bold green]", border_style="green"))
        console.print("1. Port Scanner + Banner Grab")
        console.print("2. DNS Lookup Complet")
        console.print("3. Website Scraper Avancé")
        console.print("4. Ping Tool")
        console.print("5. WiFi Networks Scanner")
        console.print("6. SSL/TLS Certificate Analyzer")   # ← NOUVEAU
        console.print("0. Retour au menu principal\n")

        choice = Prompt.ask("[bold yellow]Votre choix[/bold yellow]", choices=["0","1","2","3","4","5","6"], default="0")

        if choice == "0": break
        elif choice == "1":
            target = Prompt.ask("Cible (IP ou domaine)")
            mode = Prompt.ask("Mode", choices=["single", "range"], default="range")
            if mode == "single":
                ports = [int(Prompt.ask("Port", default="80"))]
            else:
                start = int(Prompt.ask("Port début", default="1"))
                end = int(Prompt.ask("Port fin", default="500"))
                ports = list(range(start, end + 1))
            # port_scanner(target, ports, console)  # ta fonction existante
            pass
        elif choice == "2":
            domain = Prompt.ask("Domaine")
            # dns_lookup(domain, console)
            pass
        elif choice == "3":
            url = Prompt.ask("URL du site")
            # website_scraper(url, console)
            pass
        elif choice == "4":
            target = Prompt.ask("Cible à pinger")
            # ping_tool(target, console)
            pass
        elif choice == "5":
            # wifi_scanner(console)
            pass
        elif choice == "6":
            target = Prompt.ask("Site à analyser (ex: google.com)")
            ssl_analyzer(target, console)

        input("\n[bold]Appuyez sur Entrée pour continuer...[/bold]")