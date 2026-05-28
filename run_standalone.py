"""
Standalone entry point for the SFTP transfer service.
Designed to run continuously (e.g. via scheduled task or manual execution).

Usage:
    python run_standalone.py
    Ctrl+C to stop
"""

import configparser
import os
import signal
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from alert_manager import AlertManager
from file_watcher import FileWatcher
from log_setup import setup_logging
from sftp_transfer import SFTPTransfer

CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.ini")


def load_config(path: str) -> configparser.ConfigParser:
    """Load and validate the INI configuration file."""
    if not os.path.isfile(path):
        sys.exit(f"ERREUR : fichier de configuration introuvable : {path}")

    config = configparser.ConfigParser()
    config.read(path, encoding="utf-8")

    required = ["sftp", "watch", "logging", "alerts", "retry"]
    for section in required:
        if not config.has_section(section):
            sys.exit(f"ERREUR : section [{section}] manquante dans {path}")

    if not config.get("sftp", "password", fallback=""):
        sys.exit("ERREUR : mot de passe SFTP non renseigné dans config.ini")

    return config


def build_alert_manager(config: configparser.ConfigParser) -> AlertManager:
    """Instantiate AlertManager from config."""
    return AlertManager(
        enabled=config.getboolean("alerts", "enabled", fallback=False),
        smtp_host=config.get("alerts", "smtp_host", fallback=""),
        smtp_port=config.getint("alerts", "smtp_port", fallback=587),
        smtp_use_tls=config.getboolean("alerts", "smtp_use_tls", fallback=True),
        smtp_username=config.get("alerts", "smtp_username", fallback=""),
        smtp_password=config.get("alerts", "smtp_password", fallback=""),
        from_email=config.get("alerts", "from_email", fallback=""),
        to_emails=[
            e.strip()
            for e in config.get("alerts", "to_emails", fallback="").split(",")
            if e.strip()
        ],
        subject_prefix=config.get("alerts", "subject_prefix", fallback="[ALERTE SFTP]"),
    )


def build_sftp_client(config: configparser.ConfigParser) -> SFTPTransfer:
    """Instantiate SFTPTransfer from config."""
    return SFTPTransfer(
        host=config.get("sftp", "host"),
        port=config.getint("sftp", "port", fallback=22),
        username=config.get("sftp", "username"),
        password=config.get("sftp", "password"),
        remote_directory=config.get("sftp", "remote_directory", fallback="/"),
    )


def main():
    config = load_config(CONFIG_PATH)

    logger = setup_logging(
        log_directory=config.get("logging", "log_directory"),
        log_level=config.get("logging", "log_level", fallback="INFO"),
        retention_days=config.getint("logging", "log_retention_days", fallback=90),
    )

    logger.info("=" * 60)
    logger.info("SERVICE SFTP - Démarrage (standalone)")
    logger.info("=" * 60)

    alert_mgr = build_alert_manager(config)
    sftp = build_sftp_client(config)

    logger.info("Test de connexion SFTP...")
    if sftp.test_connection():
        logger.info("Connexion SFTP OK.")
    else:
        logger.warning("Connexion SFTP échouée. Le service continuera de retenter.")

    watcher = FileWatcher(
        source_directory=config.get("watch", "source_directory"),
        file_pattern=config.get("watch", "file_pattern", fallback="*.txt"),
        archive_directory=config.get("watch", "archive_directory"),
        poll_interval=config.getint("watch", "poll_interval", fallback=30),
        sftp=sftp,
        alert_manager=alert_mgr,
        max_retries=config.getint("retry", "max_retries", fallback=3),
        retry_delay=config.getint("retry", "retry_delay", fallback=60),
    )

    def on_sigint(sig, frame):
        logger.info("Signal d'arrêt reçu...")
        watcher.stop()

    signal.signal(signal.SIGINT, on_sigint)
    signal.signal(signal.SIGTERM, on_sigint)

    # alert_mgr.send_service_start_alert()  # Désactivé - emails uniquement en cas d'alerte
    watcher.start()
    # alert_mgr.send_service_stop_alert()  # Désactivé - emails uniquement en cas d'alerte
    logger.info("Service terminé.")


if __name__ == "__main__":
    main()
