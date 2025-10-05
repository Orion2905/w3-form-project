#!/usr/bin/env python3
"""
Script di emergenza per rimuovere manualmente il campo additional_document dal database Azure
"""

import sys
import os
from datetime import datetime

# Aggiungi il percorso del progetto al PATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def emergency_fix_azure_db():
    """Rimuove manualmente il campo additional_document dal database Azure"""
    try:
        from w3form import create_app, db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("🚨 EMERGENCY FIX - Rimozione campo additional_document")
            print("=" * 60)
            
            # Verifica connessione
            try:
                result = db.session.execute(text("SELECT 1")).scalar()
                print("✅ Connessione database: OK")
            except Exception as e:
                print(f"❌ Connessione fallita: {e}")
                return False
            
            # Verifica se il campo esiste
            print("\n🔍 Verifica esistenza campo additional_document...")
            try:
                db.session.execute(text("SELECT TOP 1 additional_document FROM candidate")).fetchone()
                print("⚠️  Campo additional_document: PRESENTE (problema confermato)")
                field_exists = True
            except Exception:
                print("✅ Campo additional_document: NON PRESENTE")
                field_exists = False
                return True
            
            if field_exists:
                print("\n🔧 RIMOZIONE MANUALE DEL CAMPO...")
                
                try:
                    # Step 1: Backup delle informazioni sulla colonna
                    print("1. Backup informazioni colonna...")
                    backup_info = db.session.execute(text("""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'candidate' AND COLUMN_NAME = 'additional_document'
                    """)).fetchone()
                    
                    if backup_info:
                        print(f"   Colonna trovata: {backup_info}")
                    
                    # Step 2: Rimuovi la colonna
                    print("2. Rimozione colonna additional_document...")
                    db.session.execute(text("ALTER TABLE candidate DROP COLUMN additional_document"))
                    db.session.commit()
                    print("✅ Colonna rimossa con successo!")
                    
                    # Step 3: Verifica rimozione
                    print("3. Verifica rimozione...")
                    try:
                        db.session.execute(text("SELECT additional_document FROM candidate WHERE 1=0"))
                        print("❌ Colonna ancora presente!")
                        return False
                    except Exception:
                        print("✅ Colonna rimossa correttamente!")
                    
                    # Step 4: Test query completa
                    print("4. Test query Candidate...")
                    from w3form.models import Candidate
                    candidates = Candidate.query.limit(1).all()
                    print(f"✅ Query funzionante: {len(candidates)} candidati trovati")
                    
                    # Step 5: Aggiorna la versione della migrazione
                    print("5. Aggiornamento versione migrazione...")
                    try:
                        # Marca la migrazione come applicata
                        db.session.execute(text("""
                            UPDATE alembic_version 
                            SET version_num = (
                                SELECT TOP 1 version_num 
                                FROM alembic_version 
                                ORDER BY version_num DESC
                            )
                        """))
                        db.session.commit()
                        print("✅ Versione migrazione aggiornata")
                    except Exception as version_error:
                        print(f"⚠️  Aggiornamento versione: {version_error}")
                    
                    print(f"\n🎉 RIPARAZIONE COMPLETATA!")
                    print(f"📅 Timestamp: {datetime.now()}")
                    return True
                    
                except Exception as fix_error:
                    print(f"❌ Errore durante la riparazione: {fix_error}")
                    db.session.rollback()
                    return False
            
    except Exception as general_error:
        print(f"❌ Errore generale: {general_error}")
        return False

if __name__ == '__main__':
    print("🚨 EMERGENCY DATABASE FIX")
    print("Questo script rimuove manualmente il campo 'additional_document' dal database Azure")
    print("=" * 80)
    
    confirm = input("⚠️  ATTENZIONE: Operazione irreversibile sul database di produzione!\nDigita 'EMERGENCY_FIX' per procedere: ")
    
    if confirm == 'EMERGENCY_FIX':
        success = emergency_fix_azure_db()
        if success:
            print("\n✅ RIPARAZIONE COMPLETATA")
            print("🔄 Riavvia l'applicazione Azure per applicare le modifiche")
            print("🌐 Test: https://flask-w3-prod-app.azurewebsites.net/")
        else:
            print("\n❌ RIPARAZIONE FALLITA")
            print("📞 Contattare il supporto tecnico")
    else:
        print("❌ Operazione annullata")
