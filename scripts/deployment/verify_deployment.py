#!/usr/bin/env python3
"""
Script di verifica pre-deployment per Azure
Questo script deve essere eseguito prima del deployment per assicurarsi che tutto sia pronto
"""

import sys
import os
from datetime import datetime

def verify_deployment_readiness():
    """Verifica che l'applicazione sia pronta per il deployment"""
    print("🔍 Verifica pre-deployment per Azure")
    print("=" * 50)
    
    # 1. Verifica file essenziali
    essential_files = [
        'app.py',
        'requirements.txt',
        'startup.txt',
        'w3form/__init__.py',
        'w3form/config.py',
        'w3form/models.py',
        'w3form/routes.py'
    ]
    
    print("📁 Verifica file essenziali...")
    missing_files = []
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MANCANTE")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ File mancanti: {', '.join(missing_files)}")
        return False
    
    # 2. Verifica migrazioni
    print("\n🗃️  Verifica migrazioni...")
    if os.path.exists('migrations/versions'):
        migration_files = [f for f in os.listdir('migrations/versions') if f.endswith('.py') and f != '__pycache__']
        print(f"   📊 Trovate {len(migration_files)} migrazioni")
        for migration in sorted(migration_files)[-3:]:  # Mostra le ultime 3
            print(f"   • {migration}")
    else:
        print("   ⚠️  Cartella migrazioni non trovata")
    
    # 3. Verifica requirements.txt
    print("\n📦 Verifica requirements.txt...")
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
        essential_packages = ['Flask', 'SQLAlchemy', 'gunicorn', 'pyodbc']
        for package in essential_packages:
            if package.lower() in requirements.lower():
                print(f"   ✅ {package}")
            else:
                print(f"   ❌ {package} - MANCANTE")
    
    # 4. Test import moduli
    print("\n🐍 Test import moduli Python...")
    try:
        sys.path.insert(0, os.getcwd())
        from w3form import create_app
        print("   ✅ w3form.create_app")
        
        app = create_app()
        print("   ✅ Creazione app Flask")
        
        from w3form.models import Candidate, User, DynamicForm
        print("   ✅ Import modelli database")
        
    except Exception as e:
        print(f"   ❌ Errore import: {e}")
        return False
    
    print("\n🎉 Verifica pre-deployment completata!")
    print("✅ L'applicazione è pronta per il deployment su Azure")
    return True

def show_deployment_instructions():
    """Mostra le istruzioni per il deployment"""
    print("\n" + "=" * 50)
    print("📋 ISTRUZIONI PER IL DEPLOYMENT SU AZURE")
    print("=" * 50)
    print("1. Verifica che tutte le variabili d'ambiente siano configurate:")
    print("   • DB_USER")
    print("   • DB_PASSWORD") 
    print("   • DB_SERVER")
    print("   • DB_NAME")
    print("   • SECRET_KEY")
    print("   • AZURE_STORAGE_CONNECTION_STRING")
    print()
    print("2. Assicurati che il file startup.txt sia configurato correttamente")
    print("3. Pusha il codice su GitHub/Azure DevOps")
    print("4. Azure dovrebbe automaticamente:")
    print("   • Installare le dipendenze")
    print("   • Eseguire le migrazioni")
    print("   • Avviare l'applicazione")
    print()
    print("🔗 URL applicazione: https://flask-w3-prod-app.azurewebsites.net/")

if __name__ == '__main__':
    success = verify_deployment_readiness()
    if success:
        show_deployment_instructions()
    else:
        print("\n❌ Correggere i problemi prima del deployment")
        sys.exit(1)
