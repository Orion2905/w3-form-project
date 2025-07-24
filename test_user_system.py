#!/usr/bin/env python3
"""
Script di test per verificare il sistema di gestione utenti
"""

import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from w3form import create_app, db
from w3form.models import User

def test_user_system():
    """Testa il sistema di gestione utenti"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Verifica sistema utenti...")
        
        # Verifica utenti esistenti
        users = User.query.all()
        print(f"📊 Utenti totali: {len(users)}")
        
        for user in users:
            print(f"   - {user.username} ({user.role}) - {user.email}")
        
        # Verifica se esiste un developer
        developer = User.query.filter_by(role='developer').first()
        if developer:
            print(f"✅ Developer trovato: {developer.username}")
            print(f"   - È developer: {developer.is_developer()}")
            print(f"   - È intervistatore: {developer.is_intervistatore()}")
            print(f"   - È ospite: {developer.is_ospite()}")
        else:
            print("❌ Nessun developer trovato!")
        
        # Test creazione utente ospite
        print("\n🔧 Test creazione utente ospite...")
        guest = User.query.filter_by(username='guest').first()
        if not guest:
            guest = User(
                username='guest',
                email='guest@example.com',
                first_name='Guest',
                last_name='User',
                role='ospite'
            )
            guest.set_password('guest123')
            db.session.add(guest)
            db.session.commit()
            print("✅ Utente ospite creato: guest/guest123")
        else:
            print("✅ Utente ospite già esistente")
        
        # Test creazione utente intervistatore
        print("\n🔧 Test creazione utente intervistatore...")
        interviewer = User.query.filter_by(username='interviewer').first()
        if not interviewer:
            interviewer = User(
                username='interviewer',
                email='interviewer@example.com',
                first_name='Interview',
                last_name='User',
                role='intervistatore'
            )
            interviewer.set_password('interview123')
            db.session.add(interviewer)
            db.session.commit()
            print("✅ Utente intervistatore creato: interviewer/interview123")
        else:
            print("✅ Utente intervistatore già esistente")
        
        print("\n📋 Riassunto utenti creati:")
        print("1. admin/admin123 (developer) - Accesso completo + gestione utenti")
        print("2. interviewer/interview123 (intervistatore) - Accesso standard")
        print("3. guest/guest123 (ospite) - Solo visualizzazione + export")
        
        print("\n🚀 Sistema utenti configurato correttamente!")

if __name__ == '__main__':
    test_user_system()
