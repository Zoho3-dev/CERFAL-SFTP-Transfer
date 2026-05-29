SFTP Transfer Service - Version Sans Emails
=============================================

1. Editez config.example.ini et renommez-le en config.ini
   - Remplissez les parametres SFTP (host, username, password, remote_directory)
   - Verifiez les chemins source_directory et archive_directory
   - PAS de section [alerts] - les emails sont desactives

2. Executez install.bat en tant qu'administrateur
   - Cree les repertoires necessaires
   - Cree la tache planifiee automatiquement
   - Demarre le service

3. Pour tester manuellement: test_run.bat

4. Verifiez les logs : C:\ProgramData\SFTPService\logs\sftp_service.log

Contenu du package :
- SFTP_Service.exe    : Executable autonome (sans emails)
- config.example.ini  : Template de configuration (sans alerts)
- install.bat         : Script d'installation automatique
- test_run.bat        : Script de test manuel
- README.txt          : Ce fichier
