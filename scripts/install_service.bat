@echo off
echo ============================================
echo   Installation du service SFTP Transfer
echo ============================================
echo.

:: Vérifier les droits administrateur
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR : Ce script doit être exécuté en tant qu'Administrateur.
    echo Clic droit ^> Exécuter en tant qu'administrateur
    pause
    exit /b 1
)

:: Vérifier que Python est accessible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR : Python n'est pas trouvé dans le PATH.
    echo Installez Python 3.10+ et ajoutez-le au PATH.
    pause
    exit /b 1
)

:: Installer les dépendances
echo Installation des dépendances Python...
pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo ERREUR : Impossible d'installer les dépendances.
    pause
    exit /b 1
)
echo.

:: Créer le répertoire de logs
echo Création du répertoire de logs...
mkdir "C:\ProgramData\SFTPService\logs" 2>nul
echo.

:: Créer le répertoire d'archive
echo Création du répertoire d'archive...
mkdir "C:\ProgramData\Sage\Communication\Recus\archive" 2>nul
echo.

:: Installer le service
echo Installation du service Windows...
python "%~dp0service.py" install
if %errorlevel% neq 0 (
    echo ERREUR : Impossible d'installer le service.
    pause
    exit /b 1
)
echo.

:: Configurer le démarrage automatique
echo Configuration du démarrage automatique...
sc config SFTPTransferService start= auto
echo.

echo ============================================
echo   Installation terminée avec succès !
echo ============================================
echo.
echo Prochaines étapes :
echo   1. Compléter le mot de passe SFTP dans config.ini
echo   2. Configurer les alertes email dans config.ini
echo   3. Tester la connexion : python test_connection.py
echo   4. Démarrer le service : net start SFTPTransferService
echo.
pause
