"""Test SFTP alert by simulating a transfer failure."""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from run_standalone import load_config, build_alert_manager

def main():
    print("=" * 50)
    print("  TEST ALERTE SFTP (ÉCHEC SIMULÉ)")
    print("=" * 50)
    
    try:
        config = load_config(os.path.join(SCRIPT_DIR, "config.ini"))
        alert_mgr = build_alert_manager(config)
        
        print("EMAIL Envoi d'une alerte d'échec de transfert...")
        
        # Simuler une alerte d'échec
        alert_mgr.send_transfer_failure_alert(
            filename="test_document.txt",
            error="Connection timeout: Unable to connect to SFTP server",
            attempt=3,
            max_retries=3
        )
        
        print("OK Alerte d'échec envoyée !")
        print("Vérifiez votre boîte mail zoho3@altais.fr")
        
        print("\nEMAIL Envoi d'une alerte de succès après retry...")
        
        # Simuler une alerte de succès après retry
        alert_mgr.send_transfer_success_after_retry(
            filename="test_document.txt",
            attempt=3
        )
        
        print("OK Alerte de succès envoyée !")
        print("Vérifiez votre boîte mail zoho3@altais.fr")
        
        return 0
        
    except Exception as e:
        print(f"ERREUR : {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
