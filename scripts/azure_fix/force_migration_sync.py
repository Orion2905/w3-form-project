#!/usr/bin/env python3
"""
Script per applicare manualmente le migrazioni mancanti
Questo script forza l'applicazione delle migrazioni sul database Azure
"""

import sys
import os
from datetime import datetime

# Aggiungi il percorso del progetto al PATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def force_migration_sync():
    """Forza la sincronizzazione delle migrazioni con il database Azure"""
    try:
        from w3form import create_app, db
        from flask_migrate import upgrade, current, stamp
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("🔧 Sincronizzazione Forzata Migrazioni Azure")
            print("=" * 60)
            
            # Verifica connessione database
            try:
                result = db.session.execute(text("SELECT 1")).scalar()
                print("✅ Connessione database: OK")
            except Exception as e:
                print(f"❌ Connessione database fallita: {e}")
                return False
            
            # Verifica se la tabella candidate esiste
            try:
                db.session.execute(text("SELECT TOP 1 * FROM candidate")).fetchone()
                print("✅ Tabella candidate: Esiste")
            except Exception as e:
                print(f"⚠️  Tabella candidate: {e}")
            
            # Verifica se il campo additional_document esiste ancora
            try:
                db.session.execute(text("SELECT additional_document FROM candidate WHERE 1=0"))
                print("⚠️  Campo additional_document: Ancora presente nel database!")
                field_exists = True
            except Exception:
                print("✅ Campo additional_document: Rimosso correttamente")
                field_exists = False
            
            # Se il campo esiste ancora, applicare le migrazioni
            if field_exists:
                print("\n🔄 Applicazione migrazioni mancanti...")
                try:
                    # Forza l'applicazione di tutte le migrazioni
                    upgrade()
                    print("✅ Migrazioni applicate con successo!")
                    
                    # Verifica di nuovo il campo
                    try:
                        db.session.execute(text("SELECT additional_document FROM candidate WHERE 1=0"))
                        print("❌ Campo additional_document ancora presente dopo migrazione!")
                    except Exception:
                        print("✅ Campo additional_document rimosso con successo!")
                        
                except Exception as migration_error:
                    print(f"❌ Errore durante migrazioni: {migration_error}")
                    
                    # Tentativo di riparazione manuale
                    print("\n🔧 Tentativo riparazione manuale...")
                    try:
                        # Rimuovi manualmente il campo se la migrazione fallisce
                        db.session.execute(text("ALTER TABLE candidate DROP COLUMN additional_document"))
                        db.session.commit()
                        print("✅ Campo additional_document rimosso manualmente!")
                    except Exception as manual_error:
                        print(f"❌ Riparazione manuale fallita: {manual_error}")
                        return False
            
            # Verifica finale
            print("\n🔍 Verifica finale...")
            try:
                from w3form.models import Candidate
                candidates = Candidate.query.limit(1).all()
                print(f"✅ Query Candidate funzionante: {len(candidates)} record trovati")
            except Exception as query_error:
                print(f"❌ Query Candidate fallita: {query_error}")
                return False
            
            print(f"\n🎉 Sincronizzazione completata!")
            print(f"📅 Timestamp: {datetime.now()}")
            return True
            
    except Exception as general_error:
        print(f"❌ Errore generale: {general_error}")
        return False

if __name__ == '__main__':
    print("⚠️  ATTENZIONE: Questo script modifica il database di produzione!")
    print("Assicurati di aver fatto un backup prima di continuare.")
    
    confirm = input("\nDigita 'PROCEDI' per continuare: ")
    if confirm == 'PROCEDI':
        success = force_migration_sync()
        if success:
            print("\n✅ Operazione completata. L'applicazione Azure dovrebbe ora funzionare.")
        else:
            print("\n❌ Operazione fallita. Controlla i log per maggiori dettagli.")
    else:
        print("Operazione annullata.")
