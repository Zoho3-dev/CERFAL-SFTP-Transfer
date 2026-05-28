# Service de Transfert SFTP

Service de transfert automatique de fichiers vers un serveur SFTP distant.
Surveille un répertoire local, détecte les nouveaux fichiers et les transfère de manière sécurisée.

---

## Fonctionnalités

- Surveillance continue d'un répertoire local (polling configurable)
- Transfert SFTP sécurisé avec vérification d'intégrité
- Archivage local automatique après transfert réussi
- Mécanisme de retry avec alertes email
- Logs rotatifs quotidiens avec rétention configurable
- Deux modes d'exécution : standalone (tâche planifiée) ou service Windows

---

## Architecture

```
sftp_service/
├── run_standalone.py       # Point d'entrée principal (standalone / tâche planifiée)
├── service.py              # Wrapper service Windows (pywin32)
├── sftp_transfer.py        # Client SFTP (upload + vérification)
├── file_watcher.py         # Surveillance répertoire + retry
├── alert_manager.py        # Alertes email (SMTP / SMTP_SSL)
├── log_setup.py            # Configuration logging rotatif
├── test_connection.py      # Test de connexion rapide
├── config.ini              # Configuration (non versionné)
├── config.example.ini      # Template de configuration
├── install_service.bat     # Installation service Windows
├── uninstall_service.bat   # Désinstallation service Windows
├── requirements.txt        # Dépendances Python
└── .gitignore
```

**Flux de données :**

```
Répertoire source → FileWatcher → SFTPTransfer → Serveur SFTP
                         ↓
                  Répertoire archive (local)
```

---

## Prérequis

- Windows 10/11 ou Windows Server 2016+
- Python 3.10+
- Accès réseau au serveur SFTP

---

## Installation

```powershell
# 1. Cloner le projet
git clone <repo_url>
cd sftp_service

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Créer la configuration
copy config.example.ini config.ini
# Éditer config.ini avec les paramètres réels
```

---

## Configuration

Copier `config.example.ini` vers `config.ini` et renseigner les valeurs :

```ini
[sftp]
host = serveur.example.com
port = 22
username = utilisateur
password = mot_de_passe
remote_directory = /upload

[watch]
source_directory = C:\ProgramData\Sage\Communication\Recus
file_pattern = *.txt
poll_interval = 30
archive_directory = C:\ProgramData\Sage\Communication\Recus\archive

[logging]
log_directory = C:\ProgramData\SFTPService\logs
log_level = INFO
log_retention_days = 90

[alerts]
enabled = true
smtp_host = smtp.gmail.com
smtp_port = 587
smtp_use_tls = true
smtp_username = email@example.com
smtp_password = mot_de_passe_app
from_email = email@example.com
to_emails = admin@example.com

[retry]
max_retries = 3
retry_delay = 60
```

### Notes sur les alertes email

| Port | Méthode | Exemple |
|------|---------|---------|
| 587 | STARTTLS | Gmail, Office 365 |
| 465 | SSL implicite (SMTP_SSL) | Gmail legacy |
| 25 | Aucun chiffrement | Serveur interne |

Pour Gmail, utilisez un [mot de passe d'application](https://myaccount.google.com/apppasswords).

---

## Exécution

### Mode Standalone (recommandé pour tâche planifiée)

```powershell
python run_standalone.py
```

Arrêt : `Ctrl+C` ou signal SIGTERM.

### Mode Service Windows

```powershell
# Installation (en tant qu'Administrateur)
install_service.bat

# Démarrer / Arrêter
net start SFTPTransferService
net stop SFTPTransferService

# Statut
sc query SFTPTransferService

# Désinstallation
uninstall_service.bat
```

---

## Tâche Planifiée Windows

Pour exécuter le service via le Planificateur de tâches :

1. Ouvrir **Planificateur de tâches** (`taskschd.msc`)
2. Créer une tâche de base :
   - **Déclencheur** : Au démarrage de l'ordinateur
   - **Action** : Démarrer un programme
   - **Programme** : `python.exe`
   - **Arguments** : `C:\chemin\vers\sftp_service\run_standalone.py`
   - **Démarrer dans** : `C:\chemin\vers\sftp_service`
3. Propriétés avancées :
   - Exécuter même si l'utilisateur n'est pas connecté
   - Exécuter avec les privilèges les plus élevés
   - Redémarrer en cas d'échec (toutes les 5 minutes, 3 tentatives)

---

## Test de connexion

```powershell
python test_connection.py
```

Affiche la connectivité SFTP et liste le contenu du répertoire distant.

---

## Logs

Les logs sont dans `C:\ProgramData\SFTPService\logs\` avec rotation quotidienne.

```powershell
# Lecture en temps réel
Get-Content "C:\ProgramData\SFTPService\logs\sftp_service.log" -Wait -Tail 50

# Dernières lignes
Get-Content "C:\ProgramData\SFTPService\logs\sftp_service.log" -Tail 30
```

### Format des logs

```
2026-05-28 10:30:00 | INFO     | Nouveau fichier détecté : export.txt
2026-05-28 10:30:01 | INFO     | Transfert réussi : /upload/export.txt (4.5 Ko)
2026-05-28 10:30:01 | INFO     | Fichier archivé : export.txt -> 20260528_103001_export.txt
```

### Niveaux de log

| Niveau | Description |
|--------|-------------|
| `INFO` | Fonctionnement normal (détection, transfert, archivage) |
| `WARNING` | Connexion échouée, répertoire absent |
| `ERROR` | Échec d'une tentative de transfert |
| `CRITICAL` | Échec définitif après toutes les tentatives |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: paramiko` | `pip install -r requirements.txt` |
| `Permission denied` sur le SFTP | Vérifier les droits du répertoire distant |
| `Connection refused` | Vérifier hôte, port, et pare-feu |
| `Authentication failed` | Vérifier username/password dans `config.ini` |
| Fichiers non détectés | Vérifier `source_directory` et `file_pattern` |
| Pas de logs | Vérifier que le répertoire de logs existe |
| Service ne démarre pas | Lancer `python run_standalone.py` pour voir les erreurs |

---

## Sécurité

- **Ne jamais versionner `config.ini`** (contient des mots de passe)
- Utiliser des mots de passe d'application pour les alertes email
- Restreindre les permissions sur `config.ini` (lecture seule pour le compte de service)
- Les transferts sont chiffrés via SSH/SFTP
- Vérification d'intégrité post-transfert (comparaison taille fichier)
