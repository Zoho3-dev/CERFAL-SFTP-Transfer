"""File watcher module - monitors a directory and triggers SFTP uploads."""

import fnmatch
import logging
import os
import shutil
import time
from datetime import datetime

from alert_manager import AlertManager
from sftp_transfer import SFTPTransfer

logger = logging.getLogger("SFTPService")


class FileWatcher:
    """Polls a source directory and uploads new files via SFTP."""

    def __init__(
        self,
        source_directory: str,
        file_pattern: str,
        archive_directory: str,
        poll_interval: int,
        sftp: SFTPTransfer,
        alert_manager: AlertManager,
        max_retries: int = 3,
        retry_delay: int = 60,
    ):
        self.source_directory = source_directory
        self.file_pattern = file_pattern
        self.archive_directory = archive_directory
        self.poll_interval = poll_interval
        self.sftp = sftp
        self.alert_manager = alert_manager
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._processed_files: set[str] = set()
        self._running = False

    def start(self):
        """Start the polling loop."""
        self._running = True
        self._ensure_directories()
        self._load_already_archived()

        logger.info("Surveillance démarrée : %s | Pattern : %s | Intervalle : %ds",
                    self.source_directory, self.file_pattern, self.poll_interval)

        while self._running:
            try:
                self._scan_and_transfer()
            except Exception as exc:
                logger.error("Erreur dans la boucle de surveillance : %s", exc)
            time.sleep(self.poll_interval)

    def stop(self):
        """Signal the polling loop to stop."""
        self._running = False
        logger.info("Arrêt de la surveillance demandé.")

    def _ensure_directories(self):
        """Create source and archive directories if missing."""
        os.makedirs(self.source_directory, exist_ok=True)
        os.makedirs(self.archive_directory, exist_ok=True)

    def _load_already_archived(self):
        """Load already-archived filenames to avoid reprocessing."""
        if not os.path.isdir(self.archive_directory):
            return
        for name in os.listdir(self.archive_directory):
            # Archive format: 20260526_143000_filename.txt
            parts = name.split("_", 2)
            original_name = parts[2] if len(parts) >= 3 else name
            self._processed_files.add(original_name)
        logger.debug("Fichiers déjà archivés : %d", len(self._processed_files))

    def _scan_and_transfer(self):
        """Scan source directory and transfer new matching files."""
        if not os.path.isdir(self.source_directory):
            logger.warning("Répertoire source introuvable : %s", self.source_directory)
            return

        for filename in os.listdir(self.source_directory):
            filepath = os.path.join(self.source_directory, filename)

            if not os.path.isfile(filepath):
                continue
            if not fnmatch.fnmatch(filename.lower(), self.file_pattern.lower()):
                continue
            if os.path.getsize(filepath) == 0:
                continue
            if filename in self._processed_files:
                continue
            if not self._is_file_stable(filepath):
                logger.debug("Fichier en cours d'écriture, report : %s", filename)
                continue

            logger.info("Nouveau fichier détecté : %s", filename)
            self._transfer_with_retry(filepath, filename)

    def _is_file_stable(self, filepath: str, wait_seconds: int = 3) -> bool:
        """Check file is not being written to by comparing size over time."""
        try:
            size1 = os.path.getsize(filepath)
            time.sleep(wait_seconds)
            size2 = os.path.getsize(filepath)
            return size1 == size2
        except OSError:
            return False

    def _transfer_with_retry(self, filepath: str, filename: str):
        """Attempt file transfer with configurable retry logic."""
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Tentative %d/%d pour %s", attempt, self.max_retries, filename)
                self.sftp.upload_file(filepath)
                self._archive_file(filepath, filename)
                self._processed_files.add(filename)

                if attempt > 1:
                    self.alert_manager.send_transfer_success_after_retry(filename, attempt)

                logger.info("Fichier traité avec succès : %s", filename)
                return

            except Exception as exc:
                last_error = str(exc)
                logger.error("Échec tentative %d/%d pour %s : %s",
                             attempt, self.max_retries, filename, exc)
                if attempt < self.max_retries:
                    logger.info("Nouvelle tentative dans %ds...", self.retry_delay)
                    time.sleep(self.retry_delay)

        logger.critical("ÉCHEC DÉFINITIF pour %s après %d tentatives : %s",
                        filename, self.max_retries, last_error)
        self.alert_manager.send_transfer_failure_alert(
            filename, last_error, self.max_retries, self.max_retries
        )

    def _archive_file(self, filepath: str, filename: str):
        """Move file to archive directory with timestamp prefix."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{timestamp}_{filename}"
        archive_path = os.path.join(self.archive_directory, archive_name)
        shutil.move(filepath, archive_path)
        logger.info("Fichier archivé : %s -> %s", filename, archive_name)
