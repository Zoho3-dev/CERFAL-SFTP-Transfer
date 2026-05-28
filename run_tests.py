"""Test runner for SFTP service."""

import sys
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(SCRIPT_DIR, "tests")

def run_test(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"  Exécution de {test_file}")
    print(f"{'='*60}")
    
    test_path = os.path.join(TESTS_DIR, test_file)
    try:
        result = subprocess.run([sys.executable, test_path], 
                              cwd=SCRIPT_DIR, 
                              capture_output=True, 
                              text=True)
        print(result.stdout)
        if result.stderr:
            print("ERREURS:")
            print(result.stderr)
        return result.returncode
    except Exception as e:
        print(f"ERREUR: Impossible d'exécuter {test_file}: {e}")
        return 1

def main():
    print("SUITE DE TESTS - SERVICE SFTP")
    print("="*60)
    
    # Liste des tests à exécuter
    tests = [
        "test_connection.py",
        "test_alert_sftp.py",
    ]
    
    results = {}
    for test in tests:
        results[test] = run_test(test)
    
    # Résumé
    print(f"\n{'='*60}")
    print("RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    success_count = 0
    for test, return_code in results.items():
        status = "OK SUCCES" if return_code == 0 else "ERREUR Echec"
        print(f"{test:<25} : {status}")
        if return_code == 0:
            success_count += 1
    
    print(f"\nTotal: {success_count}/{len(tests)} tests réussis")
    
    if success_count == len(tests):
        print("\nOK Tous les tests sont passes avec succes !")
        return 0
    else:
        print(f"\nATTENTION {len(tests) - success_count} test(s) ont echoue")
        return 1

if __name__ == "__main__":
    sys.exit(main())
