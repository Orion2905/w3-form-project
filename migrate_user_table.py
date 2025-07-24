#!/usr/bin/env python3
"""
Script per aggiornare la tabella User con i nuovi campi
"""

import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from w3form import create_app, db
from w3form.models import User

def migrate_user_table():
    """Migra la tabella User aggiungendo i nuovi campi"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Aggiornamento tabella User...")
        
        try:
            # Prova ad aggiungere le colonne se non esistono
            db.engine.execute('ALTER TABLE user ADD COLUMN email VARCHAR(128) UNIQUE')
            print("✅ Aggiunta colonna email")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("ℹ️ Colonna email già esistente")
            else:
                print(f"⚠️ Errore aggiunta email: {e}")
        
        try:
            db.engine.execute('ALTER TABLE user ADD COLUMN first_name VARCHAR(64)')
            print("✅ Aggiunta colonna first_name")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("ℹ️ Colonna first_name già esistente")
            else:
                print(f"⚠️ Errore aggiunta first_name: {e}")
        
        try:
            db.engine.execute('ALTER TABLE user ADD COLUMN last_name VARCHAR(64)')
            print("✅ Aggiunta colonna last_name")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("ℹ️ Colonna last_name già esistente")
            else:
                print(f"⚠️ Errore aggiunta last_name: {e}")
        
        # Aggiorna utenti esistenti senza email
        users_without_email = User.query.filter_by(email=None).all()
        for user in users_without_email:
            if not user.email:
                user.email = f"{user.username}@example.com"
                print(f"📧 Aggiornato email per {user.username}: {user.email}")
        
        db.session.commit()
        print("✅ Migrazione completata!")
        
        # Mostra tutti gli utenti
        print("\n👥 Utenti attuali:")
        users = User.query.all()
        for user in users:
            print(f"   - {user.username} ({user.email}) - {user.first_name} {user.last_name} [{user.role}]")

if __name__ == '__main__':
    migrate_user_table()
