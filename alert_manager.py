"""Email alert manager for SFTP transfer failures and service events."""

import logging
import smtplib
import socket
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("SFTPService")


class AlertManager:
    """Sends email alerts on transfer failures and service lifecycle events."""

    def __init__(
        self,
        enabled: bool,
        smtp_host: str,
        smtp_port: int,
        smtp_use_tls: bool,
        smtp_username: str,
        smtp_password: str,
        from_email: str,
        to_emails: list[str],
        subject_prefix: str = "[ALERTE SFTP]",
    ):
        self.enabled = enabled
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_use_tls = smtp_use_tls
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.to_emails = to_emails
        self.subject_prefix = subject_prefix

    def send_alert(self, subject: str, body: str):
        """Send an email alert. Logs errors silently on failure."""
        if not self.enabled:
            return

        if not self.to_emails or not self.from_email:
            logger.warning("Configuration email incomplète, alerte non envoyée.")
            return

        full_subject = f"{self.subject_prefix} {subject}"
        hostname = socket.gethostname()
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        html_body = (
            '<html><body style="font-family: Arial, sans-serif; color: #333;">'
            '<div style="background-color: #e74c3c; color: white; padding: 15px;">'
            "<h2 style=\"margin: 0;\">Alerte Service SFTP</h2></div>"
            '<div style="border: 1px solid #ddd; padding: 20px;">'
            f"<p><strong>Serveur :</strong> {hostname}</p>"
            f"<p><strong>Date/Heure :</strong> {timestamp}</p>"
            f'<h3 style="color: #e74c3c;">{subject}</h3>'
            f'<pre style="background: #f8f9fa; padding: 15px; font-size: 13px;">{body}</pre>'
            '<p style="font-size: 11px; color: #999;">'
            f"Message automatique - Service SFTP sur {hostname}</p>"
            "</div></body></html>"
        )

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = full_subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)

            msg.attach(MIMEText(
                f"Serveur: {hostname}\nDate: {timestamp}\n\n{subject}\n\n{body}",
                "plain", "utf-8",
            ))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            self._send_smtp(msg)
            logger.info("Alerte email envoyée à %s", ", ".join(self.to_emails))

        except Exception as exc:
            logger.error("Impossible d'envoyer l'alerte email : %s", exc)

    def _send_smtp(self, msg):
        """Handle SMTP connection with proper SSL/TLS support."""
        if self.smtp_port == 465:
            # Implicit SSL (SMTP_SSL)
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, self.to_emails, msg.as_string())
        else:
            # STARTTLS or plaintext
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, self.to_emails, msg.as_string())

    def send_transfer_failure_alert(self, filename: str, error: str, attempt: int, max_retries: int):
        """Alert on transfer failure after all retries exhausted."""
        self.send_alert(
            f"Échec de transfert - {filename}",
            f"Fichier : {filename}\n"
            f"Tentative : {attempt}/{max_retries}\n"
            f"Erreur : {error}\n\n"
            f"Veuillez vérifier la connectivité et les identifiants SFTP.",
        )

    def send_transfer_success_after_retry(self, filename: str, attempt: int):
        """Notify on successful transfer after previous failures."""
        self.send_alert(
            f"Transfert réussi après {attempt} tentative(s) - {filename}",
            f"Fichier : {filename}\nRéussi à la tentative {attempt}.",
        )

    def send_service_start_alert(self):
        """Notify service start."""
        hostname = socket.gethostname()
        self.send_alert("Service SFTP démarré", f"Service démarré sur {hostname}.")

    def send_service_stop_alert(self):
        """Notify service stop."""
        hostname = socket.gethostname()
        self.send_alert("Service SFTP arrêté", f"Service arrêté sur {hostname}.")
