#!/usr/bin/env python3
"""
Script per migrare il database e aggiornare la struttura della tabella User
"""

import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from w3form import create_app, db
from w3form.models import User
from sqlalchemy import text

def migrate_database():
    """Migra il database per aggiungere i nuovi campi alla tabella User"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Inizio migrazione database...")
        
        try:
            # Verifica la struttura attuale della tabella
            print("📋 Verifica struttura tabella user...")
            
            # Controlla se le colonne esistono già
            columns_query = text("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'user'
                ORDER BY ORDINAL_POSITION
            """)
            
            existing_columns = db.session.execute(columns_query).fetchall()
            existing_column_names = [col[0] for col in existing_columns]
            
            print("Colonne attuali:")
            for col in existing_columns:
                print(f"   - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            # Aggiungi colonna email se non esiste
            if 'email' not in existing_column_names:
                print("\n➕ Aggiunta colonna email...")
                db.session.execute(text("ALTER TABLE [user] ADD email NVARCHAR(128)"))
                db.session.commit()
                print("✅ Colonna email aggiunta")
            else:
                print("✅ Colonna email già esistente")
            
            # Aggiungi colonna first_name se non esiste
            if 'first_name' not in existing_column_names:
                print("\n➕ Aggiunta colonna first_name...")
                db.session.execute(text("ALTER TABLE [user] ADD first_name NVARCHAR(64)"))
                db.session.commit()
                print("✅ Colonna first_name aggiunta")
            else:
                print("✅ Colonna first_name già esistente")
            
            # Aggiungi colonna last_name se non esiste
            if 'last_name' not in existing_column_names:
                print("\n➕ Aggiunta colonna last_name...")
                db.session.execute(text("ALTER TABLE [user] ADD last_name NVARCHAR(64)"))
                db.session.commit()
                print("✅ Colonna last_name aggiunta")
            else:
                print("✅ Colonna last_name già esistente")
            
            # Aggiorna gli utenti esistenti che non hanno email
            print("\n📧 Aggiornamento email per utenti esistenti...")
            users_without_email = db.session.execute(
                text("SELECT id, username FROM [user] WHERE email IS NULL")
            ).fetchall()
            
            for user_id, username in users_without_email:
                email = f"{username}@example.com"
                db.session.execute(
                    text("UPDATE [user] SET email = :email WHERE id = :id"),
                    {"email": email, "id": user_id}
                )
                print(f"   ✅ Aggiornato {username} -> {email}")
            
            db.session.commit()
            
            # Ora rendiamo la colonna email NOT NULL
            if 'email' in existing_column_names:
                print("\n🔒 Rendendo email NOT NULL...")
                try:
                    # Prima verifica che non ci siano valori NULL
                    null_count = db.session.execute(
                        text("SELECT COUNT(*) FROM [user] WHERE email IS NULL")
                    ).scalar()
                    
                    if null_count == 0:
                        # Aggiungi constraint NOT NULL
                        db.session.execute(text("ALTER TABLE [user] ALTER COLUMN email NVARCHAR(128) NOT NULL"))
                        db.session.commit()
                        print("✅ Email ora è NOT NULL")
                    else:
                        print(f"⚠️ Ancora {null_count} utenti senza email, salto constraint")
                except Exception as e:
                    print(f"⚠️ Errore rendendo email NOT NULL: {e}")
            
            # Aggiungi constraint UNIQUE per email se non esiste
            print("\n🔑 Aggiunta constraint UNIQUE per email...")
            try:
                db.session.execute(text("ALTER TABLE [user] ADD CONSTRAINT UQ_user_email UNIQUE (email)"))
                db.session.commit()
                print("✅ Constraint UNIQUE aggiunto per email")
            except Exception as e:
                if "already exists" in str(e) or "duplicate" in str(e).lower():
                    print("✅ Constraint UNIQUE già esistente per email")
                else:
                    print(f"⚠️ Errore aggiunta constraint UNIQUE: {e}")
            
            print("\n🎯 Verifica finale...")
            # Mostra tutti gli utenti
            users = User.query.all()
            print(f"👥 Totale utenti: {len(users)}")
            for user in users:
                print(f"   - {user.username} | {getattr(user, 'email', 'N/A')} | {getattr(user, 'first_name', 'N/A')} {getattr(user, 'last_name', 'N/A')} | {user.role}")
            
            print("\n🚀 Migrazione completata!")
            
        except Exception as e:
            print(f"❌ Errore durante la migrazione: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_database()
