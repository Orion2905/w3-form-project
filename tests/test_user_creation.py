#!/usr/bin/env python3
"""
Script per testare la creazione di un utente
"""

import sys
import os

# Aggiungi il percorso del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from w3form.models import db, User

def test_user_creation():
    """Testa la creazione di un utente"""
    with app.app_context():
        try:
            # Prova a creare un utente di test
            test_user = User(
                username='test_user',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role='intervistatore'
            )
            test_user.set_password('password123')
            
            # Prova a salvare nel database
            db.session.add(test_user)
            db.session.commit()
            
            print("✓ Utente creato con successo!")
            print(f"ID: {test_user.id}")
            print(f"Username: {test_user.username}")
            print(f"Email: {test_user.email}")
            print(f"Nome: {test_user.first_name}")
            print(f"Cognome: {test_user.last_name}")
            print(f"Ruolo: {test_user.role}")
            
            # Rimuovi l'utente di test
            db.session.delete(test_user)
            db.session.commit()
            print("✓ Utente di test rimosso")
            
            return True
            
        except Exception as e:
            print(f"✗ Errore durante la creazione dell'utente: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    test_user_creation()
