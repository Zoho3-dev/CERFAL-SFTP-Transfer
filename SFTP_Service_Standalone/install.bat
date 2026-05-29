@echo off
echo ============================================
echo   Installation SFTP Transfer Service
echo ============================================
echo.

:: Verifier les droits administrateur
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR : Executez en tant qu'Administrateur.
    pause
    exit /b 1
)

:: Creer les repertoires necessaires
echo Creation des repertoires...
mkdir "C:\ProgramData\SFTPService\logs" 2>nul
mkdir "C:\ProgramData\Sage\Communication\Recus\archive" 2>nul
echo OK.
echo.

:: Creer config.ini si absent
if not exist "%~dp0config.ini" (
    if exist "%~dp0config.example.ini" (
        copy "%~dp0config.example.ini" "%~dp0config.ini"
        echo config.ini cree depuis le template.
        echo IMPORTANT : Editez config.ini avec vos parametres SFTP.
        echo.
        notepad "%~dp0config.ini"
    )
)

:: Creer la tache planifiee
echo Creation de la tache planifiee...
schtasks /create /tn "SFTP Transfer Service" /tr "\"%~dp0SFTP_Service.exe\"" /sc onstart /ru SYSTEM /rl highest /f
if %errorlevel% neq 0 (
    echo ERREUR : Creation de la tache planifiee echouee.
    echo Creez-la manuellement via taskschd.msc
) else (
    echo Tache planifiee creee avec succes.
)
echo.

:: Demarrer la tache
echo Demarrage du service...
schtasks /run /tn "SFTP Transfer Service"
echo.

echo ============================================
echo   Installation terminee !
echo ============================================
echo.
echo Verifiez les logs : C:\ProgramData\SFTPService\logs\
echo.
pause
