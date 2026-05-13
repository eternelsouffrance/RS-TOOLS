# modules/system_tools.py
import platform
import socket
import uuid
import psutil
import os
import subprocess
import json
import logging
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

console = Console()

def save_system_result(data: dict, tool_name: str):
    try:
        filename = f"system_{tool_name}_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Résultat système sauvegardé → {filename}")
    except Exception as e:
        logging.error(f"Erreur sauvegarde : {e}")


# ====================== INFOS SYSTÈME COMPLÈTES ======================
def get_full_system_info(console: Console):
    console.status("[cyan]Collecte des informations système avancées...[/cyan]", spinner="dots").start()
    
    # Infos de base
    info = {
        "OS": f"{platform.system()} {platform.release()} ({platform.version()})",
        "Architecture": platform.machine(),
        "Hostname": socket.gethostname(),
        "Local IP": socket.gethostbyname(socket.gethostname()),
        "MAC Address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1]),
        "Username": os.getlogin(),
        "Python Version": platform.python_version(),
        "Uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
    }

    # CPU
    cpu = {
        "Cores Physiques": psutil.cpu_count(logical=False),
        "Cores Logiques": psutil.cpu_count(logical=True),
        "Utilisation CPU": f"{psutil.cpu_percent(interval=0.5)}%",
        "Fréquence": f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "N/A"
    }

    # RAM
    ram = psutil.virtual_memory()
    ram_info = {
        "RAM Totale": f"{ram.total / (1024**3):.2f} GB",
        "RAM Utilisée": f"{ram.used / (1024**3):.2f} GB ({ram.percent}%)",
        "RAM Disponible": f"{ram.available / (1024**3):.2f} GB"
    }

    # Disque
    disk = psutil.disk_usage('/')
    disk_info = {
        "Disque Total": f"{disk.total / (1024**3):.2f} GB",
        "Disque Utilisé": f"{disk.used / (1024**3):.2f} GB ({disk.percent}%)",
        "Disque Libre": f"{disk.free / (1024**3):.2f} GB"
    }

    # Réseau
    net = psutil.net_if_addrs()
    net_info = [f"{iface} → {addr.address}" for iface, addrs in net.items() for addr in addrs if addr.family == 2]

    # Batterie
    battery = psutil.sensors_battery()
    bat_info = {
        "Batterie": f"{battery.percent}% {'(En charge)' if battery.power_plugged else '(Sur batterie)'}" if battery else "Non détectée (PC fixe)"
    }

    # Affichage
    table = Table(title="🖥️  SYSTEM INFORMATION v1.5", style="bright_yellow")
    table.add_column("Catégorie", style="cyan")
    table.add_column("Détails")

    for k, v in info.items():
        table.add_row(k, str(v))
    for k, v in cpu.items():
        table.add_row(k, str(v))
    for k, v in ram_info.items():
        table.add_row(k, str(v))
    for k, v in disk_info.items():
        table.add_row(k, str(v))
    table.add_row("Interfaces Réseau", "\n".join(net_info[:6]))
    table.add_row("Batterie", bat_info["Batterie"])

    console.print(table)
    save_system_result({**info, **cpu, **ram_info, **disk_info, "battery": bat_info}, "full_info")


# ====================== PROCESSUS ======================
def list_processes(console: Console):
    console.status("[cyan]Récupération des processus en cours...[/cyan]", spinner="dots").start()
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(proc.info)
        except:
            pass

    table = Table(title="⚙️ Processus en Cours", style="magenta")
    table.add_column("PID"); table.add_column("Nom"); table.add_column("CPU %"); table.add_column("RAM %")
    
    for p in sorted(procs, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:30]:
        table.add_row(str(p['pid']), p['name'], f"{p['cpu_percent']:.1f}", f"{p['memory_percent']:.1f}")
    
    console.print(table)

    if Prompt.ask("Tuer un processus ?", choices=["y","n"], default="n") == "y":
        pid = int(Prompt.ask("PID du processus"))
        try:
            psutil.Process(pid).terminate()
            console.print(f"[green]Processus {pid} terminé.[/green]")
        except Exception as e:
            console.print(f"[red]Impossible de tuer le processus : {e}[/red]")


# ====================== TEMPÉRATURES ======================
def get_temperatures(console: Console):
    console.status("[cyan]Lecture des températures matérielles...[/cyan]", spinner="dots").start()
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            console.print("[yellow]Aucun capteur de température détecté.[/yellow]")
            return
        table = Table(title="🌡️ Températures Matérielles", style="red")
        table.add_column("Capteur"); table.add_column("Température °C")
        for name, entries in temps.items():
            for entry in entries:
                table.add_row(f"{name} {entry.label or ''}", f"{entry.current:.1f}")
        console.print(table)
    except:
        console.print("[yellow]Impossible de lire les températures (privilèges ou capteurs manquants).[/yellow]")


# ====================== MENU SYSTEM ======================
def system_menu(console: Console):
    while True:
        console.clear()
        console.print(Panel("[bold yellow]MODULE SYSTEM v1.5 - Diagnostic Avancé[/bold yellow]", border_style="yellow"))
        console.print("1. Informations Système Complètes")
        console.print("2. Liste des Processus + Kill")
        console.print("3. Températures Matérielles")
        console.print("4. Infos Batterie & Réseau")
        console.print("0. Retour au menu principal\n")

        choice = Prompt.ask("[bold yellow]Votre choix[/bold yellow]", choices=["0","1","2","3","4"], default="0")

        if choice == "0":
            break
        elif choice == "1":
            get_full_system_info(console)
        elif choice == "2":
            list_processes(console)
        elif choice == "3":
            get_temperatures(console)
        elif choice == "4":
            # Infos batterie + réseau rapide
            battery = psutil.sensors_battery()
            console.print(Panel(
                f"Batterie : {battery.percent}% {'(En charge)' if battery.power_plugged else '' if battery else 'Non détectée'}\n"
                f"IP Locale : {socket.gethostbyname(socket.gethostname())}\n"
                f"Uptime : {str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]}",
                title="📊 Infos Rapides", border_style="blue"
            ))

        input("\n[bold]Appuyez sur Entrée pour continuer...[/bold]")