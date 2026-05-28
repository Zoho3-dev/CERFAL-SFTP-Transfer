# Scripts Windows Service

Ce dossier contient les fichiers pour installer et gérer le service Windows SFTP.

## ⚠️  Important

**Pour la production, il est recommandé d'utiliser une tâche planifiée plutôt qu'un service Windows :**

- Plus simple à déployer
- Pas besoin de droits admin
- Facile à déboguer
- Moins de complexité

## Fichiers

| Fichier | Usage |
|---------|-------|
| `install_service.bat` | Installation du service Windows |
| `uninstall_service.bat` | Désinstallation du service Windows |
| `service.py` | Code du service Windows |
| `README.md` | Ce fichier |

## Installation (si vous voulez vraiment utiliser le service)

1. **Exécuter en tant qu'Administrateur** :
   ```cmd
   install_service.bat
   ```

2. **Démarrer le service** :
   ```cmd
   net start SFTPTransferService
   ```

3. **Vérifier le statut** :
   ```cmd
   sc query SFTPTransferService
   ```

## Désinstallation

```cmd
uninstall_service.bat
```

## Alternative recommandée : Tâche planifiée

Utilisez `run_standalone.py` avec le Planificateur de tâches Windows :

1. Ouvrir `taskschd.msc`
2. Créer une tâche de base
3. Déclencheur : Au démarrage
4. Action : `python run_standalone.py`
5. Exécuter même si utilisateur non connecté

C'est plus simple et plus fiable !
