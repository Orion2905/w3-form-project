#!/usr/bin/env python3
"""
Script per verificare e aggiornare le migrazioni del database su Azure
"""

import sys
import os
from datetime import datetime

# Aggiungi il percorso del progetto al PATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def check_and_update_migrations():
    """Verifica e aggiorna le migrazioni del database"""
    try:
        from w3form import create_app, db
        from flask_migrate import upgrade, current, show
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Verifica stato migrazioni database...")
            print("=" * 50)
            
            try:
                # Verifica la revisione corrente
                current_revision = current()
                print(f"📍 Revisione corrente: {current_revision}")
                
                # Applica le migrazioni pending
                print("\n🔄 Applicazione migrazioni...")
                upgrade()
                print("✅ Migrazioni applicate con successo!")
                
                # Verifica la nuova revisione
                new_revision = current()
                print(f"📍 Nuova revisione: {new_revision}")
                
            except Exception as migration_error:
                print(f"❌ Errore durante le migrazioni: {migration_error}")
                return False
                
            # Test connessione database
            print("\n🔗 Test connessione database...")
            try:
                result = db.session.execute(db.text("SELECT 1")).scalar()
                if result == 1:
                    print("✅ Connessione database: OK")
                else:
                    print("❌ Connessione database: FALLITA")
                    return False
            except Exception as db_error:
                print(f"❌ Errore connessione database: {db_error}")
                return False
            
            # Test creazione tabelle
            print("\n📋 Verifica tabelle database...")
            try:
                from w3form.models import Candidate, DynamicForm, User
                
                # Test query semplici
                candidate_count = Candidate.query.count()
                form_count = DynamicForm.query.count()
                user_count = User.query.count()
                
                print(f"   • Candidati: {candidate_count}")
                print(f"   • Form: {form_count}")
                print(f"   • Utenti: {user_count}")
                print("✅ Tabelle database: OK")
                
            except Exception as table_error:
                print(f"❌ Errore verifica tabelle: {table_error}")
                return False
            
            print("\n🎉 Verifica completata con successo!")
            return True
            
    except ImportError as import_error:
        print(f"❌ Errore import moduli: {import_error}")
        return False
    except Exception as general_error:
        print(f"❌ Errore generale: {general_error}")
        return False

if __name__ == '__main__':
    success = check_and_update_migrations()
    if not success:
        print("\n🚨 AZIONE RICHIESTA: Verificare la configurazione dell'ambiente Azure")
        sys.exit(1)
    else:
        print("\n✅ Sistema pronto per il deployment su Azure")
