"""
Windows Service wrapper for the SFTP transfer service.

Usage:
    python service.py install   - Install the service
    python service.py start     - Start the service
    python service.py stop      - Stop the service
    python service.py remove    - Uninstall the service
    python service.py debug     - Run in console mode (debug)
"""

import os
import sys

import servicemanager
import win32event
import win32service
import win32serviceutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from alert_manager import AlertManager
from file_watcher import FileWatcher
from log_setup import setup_logging
from run_standalone import build_alert_manager, build_sftp_client, load_config
from sftp_transfer import SFTPTransfer

CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.ini")


class SFTPTransferService(win32serviceutil.ServiceFramework):
    """Windows service that monitors a directory and uploads files via SFTP."""

    _svc_name_ = "SFTPTransferService"
    _svc_display_name_ = "Service SFTP Transfer"
    _svc_description_ = (
        "Surveille un répertoire local et transfère automatiquement "
        "les fichiers vers un serveur SFTP distant."
    )

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.watcher = None
        self.logger = None

    def SvcStop(self):
        """Called when Windows requests service stop."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.watcher:
            self.watcher.stop()
        if self.logger:
            self.logger.info("Service arrêté par Windows.")

    def SvcDoRun(self):
        """Service entry point."""
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )
            self._main()
        except Exception as exc:
            servicemanager.LogErrorMsg(f"SFTPTransferService erreur fatale : {exc}")

    def _main(self):
        """Core service logic."""
        config = load_config(CONFIG_PATH)

        self.logger = setup_logging(
            log_directory=config.get("logging", "log_directory"),
            log_level=config.get("logging", "log_level", fallback="INFO"),
            retention_days=config.getint("logging", "log_retention_days", fallback=90),
        )

        self.logger.info("=" * 60)
        self.logger.info("SERVICE SFTP - Démarrage (Windows Service)")
        self.logger.info("=" * 60)

        alert_mgr = build_alert_manager(config)
        sftp = build_sftp_client(config)

        if not sftp.test_connection():
            self.logger.critical("Connexion SFTP impossible au démarrage.")
            alert_mgr.send_alert(
                "Échec de connexion au démarrage",
                f"Hôte : {config.get('sftp', 'host')}:{config.getint('sftp', 'port', fallback=22)}\n"
                "Le service va continuer et retenter les connexions.",
            )

        # alert_mgr.send_service_start_alert()  # Désactivé - emails uniquement en cas d'alerte

        self.watcher = FileWatcher(
            source_directory=config.get("watch", "source_directory"),
            file_pattern=config.get("watch", "file_pattern", fallback="*.txt"),
            archive_directory=config.get("watch", "archive_directory"),
            poll_interval=config.getint("watch", "poll_interval", fallback=30),
            sftp=sftp,
            alert_manager=alert_mgr,
            max_retries=config.getint("retry", "max_retries", fallback=3),
            retry_delay=config.getint("retry", "retry_delay", fallback=60),
        )

        self.watcher.start()

        # alert_mgr.send_service_stop_alert()  # Désactivé - emails uniquement en cas d'alerte
        self.logger.info("Service terminé proprement.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SFTPTransferService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SFTPTransferService)
