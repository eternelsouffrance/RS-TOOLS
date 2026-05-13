#!/bin/bash

# ====================== RS TOOLS - INSTALLATEUR LINUX ======================
clear
echo -e "\033[1;36m========================================================\033[0m"
echo -e "\033[1;32m          RS TOOLS - INSTALLATEUR LINUX\033[0m"
echo -e "\033[1;33m      Aucune limite. Aucun bug. Aucune échappatoire.\033[0m"
echo -e "\033[1;36m========================================================\033[0m"
echo ""

# Vérification Python
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[ERREUR] Python3 n'est pas installé.\033[0m"
    echo "Installez Python avec : sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo -e "\033[1;32m[✓] Python3 détecté\033[0m"

# Création de l'environnement virtuel
if [ ! -d "venv" ]; then
    echo -e "\033[1;34m[i] Création de l'environnement virtuel...\033[0m"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "\033[1;31m[ERREUR] Impossible de créer venv\033[0m"
        exit 1
    fi
    echo -e "\033[1;32m[✓] Environnement virtuel créé\033[0m"
else
    echo -e "\033[1;32m[✓] Environnement virtuel déjà existant\033[0m"
fi

# Activation du venv
source venv/bin/activate
echo -e "\033[1;32m[✓] Environnement virtuel activé\033[0m"

# Mise à jour de pip
echo -e "\033[1;34m[i] Mise à jour de pip...\033[0m"
python -m pip install --upgrade pip --quiet

# Installation des dépendances
echo -e "\033[1;34m[i] Installation des dépendances...\033[0m"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "\033[1;33m[ATTENTION] Tentative d'installation manuelle...\033[0m"
    pip install rich requests psutil dnspython beautifulsoup4 python-whois colorama
fi

echo ""
echo -e "\033[1;36m========================================================\033[0m"
echo -e "\033[1;32m[✓] Installation terminée avec succès !\033[0m"
echo -e "\033[1;36m========================================================\033[0m"
echo ""

echo -e "\033[1;33m[i] Lancement de RS TOOLS...\033[0m"
sleep 1.5

# Lancement du programme
python main.py