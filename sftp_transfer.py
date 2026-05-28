"""SFTP file transfer module."""

import logging
import os

import paramiko

logger = logging.getLogger("SFTPService")


class SFTPTransfer:
    """Handles secure file uploads to a remote SFTP server."""

    def __init__(self, host: str, port: int, username: str, password: str, remote_directory: str = "/"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.remote_directory = remote_directory

    def _connect(self) -> tuple[paramiko.Transport, paramiko.SFTPClient]:
        """Establish SSH transport and return (transport, sftp_client)."""
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return transport, sftp

    def upload_file(self, local_path: str) -> str:
        """Upload a local file to the SFTP server. Returns remote path on success."""
        filename = os.path.basename(local_path)
        remote_path = self.remote_directory.rstrip("/") + "/" + filename

        logger.info("Connexion SFTP vers %s:%d", self.host, self.port)
        transport, sftp = self._connect()
        try:
            file_size = os.path.getsize(local_path)
            logger.info("Transfert : %s (%s) -> %s", local_path, _human_size(file_size), remote_path)
            sftp.put(local_path, remote_path)

            # Integrity check: compare remote size
            remote_stat = sftp.stat(remote_path)
            if remote_stat.st_size != file_size:
                raise IOError(
                    f"Taille incohérente après transfert : local={file_size}, distant={remote_stat.st_size}"
                )

            logger.info("Transfert réussi : %s (%s)", remote_path, _human_size(file_size))
            return remote_path
        finally:
            sftp.close()
            transport.close()

    def test_connection(self) -> bool:
        """Test SFTP connectivity. Returns True if successful."""
        try:
            transport, sftp = self._connect()
            sftp.listdir(self.remote_directory)
            sftp.close()
            transport.close()
            logger.info("Connexion SFTP OK.")
            return True
        except Exception as exc:
            logger.error("Échec connexion SFTP : %s", exc)
            return False


def _human_size(num_bytes: int) -> str:
    """Convert bytes to human-readable size string."""
    for unit in ("o", "Ko", "Mo", "Go"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} To"
