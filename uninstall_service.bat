@echo off
echo ============================================
echo   Désinstallation du service SFTP Transfer
echo ============================================
echo.

:: Vérifier les droits administrateur
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR : Ce script doit être exécuté en tant qu'Administrateur.
    pause
    exit /b 1
)

:: Arrêter le service s'il tourne
echo Arrêt du service...
net stop SFTPTransferService 2>nul
echo.

:: Désinstaller le service
echo Désinstallation du service...
python "%~dp0service.py" remove
echo.

echo ============================================
echo   Désinstallation terminée.
echo ============================================
echo.
echo Note : Les logs dans C:\ProgramData\SFTPService\logs
echo        et les archives n'ont PAS été supprimés.
echo.
pause
