@echo off
chcp 65001 >nul
title RS TOOLS - Installation Automatique
color 0b
echo.
echo ========================================================
echo          RS TOOLS - INSTALLATEUR AUTOMATIQUE
echo      Aucune limite. Aucun bug. Aucune échappatoire.
echo ========================================================
echo.

:: Vérification Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERREUR] Python non détecté dans le PATH.
    pause
    exit /b 1
)
echo [✓] Python détecté.

:: Environnement virtuel
if not exist "venv" (
    echo [i] Création de l'environnement virtuel...
    python -m venv venv
)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [✓] venv activé.
)

:: Mise à jour pip
echo [i] Mise à jour de pip...
python -m pip install --upgrade pip --quiet

:: Installation des dépendances
echo [i] Installation des dépendances...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    pip install rich requests psutil dnspython beautifulsoup4 python-whois colorama
)

echo.
echo ========================================================
echo [✓] Installation des packages terminée !
echo ========================================================
echo.

:: ====================== CONFIGURATION DU SURNOM ======================
echo [i] Configuration du surnom
if exist "config.json" (
    echo Un fichier de configuration existe déjà.
    set /p "change=Veux-tu changer ton surnom ? (O/N) : "
    if /i "!change!"=="N" goto :launch
)

set /p "nickname=Comment veux-tu que RS TOOLS t'appelle ? (ex: kripi, Shadow, Neo...) : "

if "%nickname%"=="" set nickname=Utilisateur

:: Création / Mise à jour de config.json
(
echo {
echo     "max_webhook_spam": 50,
echo     "default_delay": 1.0,
echo     "theme": "dark",
echo     "nickname": "%nickname%"
echo }
) > config.json

echo [✓] Ton surnom a été enregistré : %nickname%

:launch
echo.
echo [i] Lancement de RS TOOLS...
timeout /t 2 >nul
python main.py
pause