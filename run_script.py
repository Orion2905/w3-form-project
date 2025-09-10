#!/usr/bin/env python3
"""
Main script runner for W3 Form Project
=====================================

Questo script fornisce un'interfaccia semplice per eseguire
i vari script di utilità del progetto.

Utilizzo:
    python run_script.py setup        # Esegue setup completo
    python run_script.py test-data    # Aggiunge dati di test
    python run_script.py migrate      # Esegue migrazioni
    python run_script.py --help       # Mostra aiuto
"""

import sys
import os
import subprocess
from pathlib import Path

# Aggiungi la root del progetto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_setup():
    """Esegue il setup completo del progetto"""
    print("🚀 Avviando setup completo del progetto...")
    scripts = [
        "scripts/setup/quick_setup.py",
        "scripts/setup/init_settings.py",
        "scripts/setup/create_admin_user.py"
    ]
    
    for script in scripts:
        print(f"\n📜 Eseguendo {script}...")
        try:
            subprocess.run([sys.executable, script], cwd=project_root, check=True)
            print(f"✅ {script} completato con successo")
        except subprocess.CalledProcessError as e:
            print(f"❌ Errore nell'esecuzione di {script}: {e}")
            return False
    
    print("\n🎉 Setup completo terminato!")
    return True

def run_test_data():
    """Aggiunge dati di test al database"""
    print("📊 Aggiungendo dati di test...")
    scripts = [
        "scripts/test_data/add_test_users.py",
        "scripts/test_data/add_test_candidates.py",
        "scripts/test_data/add_test_data_fields.py"
    ]
    
    for script in scripts:
        script_path = project_root / script
        if script_path.exists():
            print(f"\n📜 Eseguendo {script}...")
            try:
                subprocess.run([sys.executable, script], cwd=project_root, check=True)
                print(f"✅ {script} completato con successo")
            except subprocess.CalledProcessError as e:
                print(f"❌ Errore nell'esecuzione di {script}: {e}")
        else:
            print(f"⚠️ Script {script} non trovato, saltato")
    
    print("\n🎉 Dati di test aggiunti!")

def run_migrations():
    """Esegue le migrazioni del database"""
    print("🔄 Eseguendo migrazioni database...")
    scripts = [
        "scripts/migration/migrate_user_table.py",
        "scripts/migration/fix_database_migration.py"
    ]
    
    for script in scripts:
        script_path = project_root / script
        if script_path.exists():
            print(f"\n📜 Eseguendo {script}...")
            try:
                subprocess.run([sys.executable, script], cwd=project_root, check=True)
                print(f"✅ {script} completato con successo")
            except subprocess.CalledProcessError as e:
                print(f"❌ Errore nell'esecuzione di {script}: {e}")
        else:
            print(f"⚠️ Script {script} non trovato, saltato")
    
    print("\n🎉 Migrazioni completate!")

def run_tests():
    """Esegue i test del progetto"""
    print("🧪 Eseguendo test...")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                      cwd=project_root, check=True)
        print("\n✅ Test completati con successo!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Alcuni test sono falliti: {e}")
    except FileNotFoundError:
        print("\n⚠️ pytest non installato. Installa con: pip install pytest")

def show_help():
    """Mostra l'help dei comandi disponibili"""
    help_text = """
🔧 W3 Form Project - Script Runner
=================================

Comandi disponibili:

  setup       - Esegue setup completo del progetto
  test-data   - Aggiunge dati di test al database  
  migrate     - Esegue migrazioni del database
  test        - Esegue tutti i test del progetto
  help        - Mostra questo messaggio di aiuto

Esempi:
  python run_script.py setup
  python run_script.py test-data
  python run_script.py migrate
  python run_script.py test

Per script specifici, naviga nelle cartelle:
  scripts/setup/     - Script di inizializzazione
  scripts/migration/ - Script di migrazione DB
  scripts/test_data/ - Script per dati di test
  tests/             - Test del progetto
"""
    print(help_text)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['setup']:
        run_setup()
    elif command in ['test-data', 'testdata']:
        run_test_data()
    elif command in ['migrate', 'migration']:
        run_migrations()
    elif command in ['test', 'tests']:
        run_tests()
    elif command in ['help', '--help', '-h']:
        show_help()
    else:
        print(f"❌ Comando sconosciuto: {command}")
        print("💡 Usa 'python run_script.py help' per vedere i comandi disponibili")

if __name__ == '__main__':
    main()
