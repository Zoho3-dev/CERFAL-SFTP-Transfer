@echo off
cd /d "%~dp0"
echo ============================================
echo   TEST DU SERVICE SFTP
echo ============================================
echo.
echo Repertoire: %~dp0
echo.

if not exist "config.ini" (
    echo ERREUR: config.ini non trouve !
    echo.
    echo Fichiers dans ce dossier:
    dir /b
    echo.
    pause
    exit /b 1
)

echo Fichier config.ini trouve.
echo Lancement du service...
echo.
echo Pour arreter: Ctrl+C puis fermer la fenetre
echo.

SFTP_Service.exe

if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Le service s'est arrete avec le code %errorlevel%
    pause
) else (
    echo.
    echo Service termine.
    pause
)
