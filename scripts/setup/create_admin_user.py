#!/usr/bin/env python3
"""
Script per creare un utente developer di default
"""

import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from w3form import create_app, db
from w3form.models import User

def create_default_developer():
    """Crea un utente developer di default"""
    app = create_app()
    
    with app.app_context():
        # Controlla se esiste già un developer
        existing_developer = User.query.filter_by(role='developer').first()
        if existing_developer:
            print(f"Utente developer già esistente: {existing_developer.username}")
            return
        
        # Crea nuovo utente developer
        developer = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='developer'
        )
        developer.set_password('admin123')
        
        db.session.add(developer)
        db.session.commit()
        
        print("✅ Utente developer creato con successo!")
        print("Username: admin")
        print("Password: admin123")
        print("Ruolo: developer")

if __name__ == '__main__':
    create_default_developer()
