"""
Quick SFTP connection test.
Usage: python test_connection.py
"""

import os
import sys

import paramiko

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from run_standalone import load_config, build_sftp_client

CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.ini")


def main():
    print("=" * 50)
    print("  TEST DE CONNEXION SFTP")
    print("=" * 50)

    config = load_config(CONFIG_PATH)

    host = config.get("sftp", "host")
    port = config.getint("sftp", "port", fallback=22)
    username = config.get("sftp", "username")
    remote_dir = config.get("sftp", "remote_directory", fallback="/")

    print(f"\n  Hôte            : {host}")
    print(f"  Port            : {port}")
    print(f"  Utilisateur     : {username}")
    print(f"  Répertoire      : {remote_dir}")
    print()

    print("Connexion en cours...")
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=config.get("sftp", "password"))
        sftp_client = paramiko.SFTPClient.from_transport(transport)

        print("✓ Connexion SSH établie.")

        print(f"\nContenu du répertoire distant '{remote_dir}' :")
        items = sftp_client.listdir_attr(remote_dir)
        if items:
            for item in items[:20]:
                size = f"{item.st_size:>10} o" if item.st_size else "     <DIR>"
                print(f"  {size}  {item.filename}")
            if len(items) > 20:
                print(f"  ... et {len(items) - 20} autres éléments")
        else:
            print("  (répertoire vide)")

        sftp_client.close()
        transport.close()
        print("\n✓ TEST RÉUSSI - Connexion SFTP fonctionnelle.")
        return 0

    except Exception as exc:
        print(f"\n✗ ÉCHEC DE CONNEXION : {exc}")
        print("\nVérifiez :")
        print("  1. Hôte et port corrects")
        print("  2. Identifiants corrects")
        print("  3. Serveur SFTP accessible")
        print("  4. Aucun pare-feu ne bloque le port")
        return 1


if __name__ == "__main__":
    sys.exit(main())
