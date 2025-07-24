#!/usr/bin/env python3
"""
Script per testare il sistema di gestione utenti completo
"""

import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from w3form import create_app, db
from w3form.models import User

def test_complete_user_system():
    """Test completo del sistema utenti"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Test sistema utenti completo...")
        
        # 1. Verifica schema tabella
        print("\n📋 Schema tabella User:")
        try:
            columns = db.engine.execute("PRAGMA table_info(user)").fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        except Exception as e:
            print(f"   ⚠️ Errore lettura schema: {e}")
        
        # 2. Crea utenti di test se non esistono
        print("\n🔧 Creazione utenti di test...")
        
        # Developer
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Super',
                last_name='Admin',
                role='developer'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Creato utente admin (developer)")
        
        # Intervistatore
        if not User.query.filter_by(username='interviewer').first():
            interviewer = User(
                username='interviewer',
                email='interviewer@example.com',
                first_name='John',
                last_name='Doe',
                role='intervistatore'
            )
            interviewer.set_password('interview123')
            db.session.add(interviewer)
            print("✅ Creato utente interviewer")
        
        # Ospite
        if not User.query.filter_by(username='guest').first():
            guest = User(
                username='guest',
                email='guest@example.com',
                first_name='Jane',
                last_name='Smith',
                role='ospite'
            )
            guest.set_password('guest123')
            db.session.add(guest)
            print("✅ Creato utente guest (ospite)")
        
        db.session.commit()
        
        # 3. Verifica tutti gli utenti
        print("\n👥 Utenti nel sistema:")
        users = User.query.all()
        for user in users:
            email = getattr(user, 'email', 'N/A')
            first_name = getattr(user, 'first_name', 'N/A')
            last_name = getattr(user, 'last_name', 'N/A')
            
            print(f"   - {user.username}")
            print(f"     📧 Email: {email}")
            print(f"     👤 Nome: {first_name} {last_name}")
            print(f"     🔐 Ruolo: {user.role}")
            print(f"     📅 Creato: {user.created_at}")
            print(f"     ✅ Metodi: dev={user.is_developer()}, int={user.is_intervistatore()}, osp={user.is_ospite()}")
            print()
        
        # 4. Test funzionalità
        print("🧪 Test funzionalità:")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"   ✅ Password check: {admin.check_password('admin123')}")
            print(f"   ✅ È developer: {admin.is_developer()}")
        
        print("\n🎯 Test URL:")
        print("   - Login: http://localhost:5000/login")
        print("   - Dashboard: http://localhost:5000/")
        print("   - Gestione Utenti (solo developer): http://localhost:5000/gestione-utenti")
        print("   - Elenco Candidati: http://localhost:5000/candidati")
        print("   - Export Candidati Multipli: http://localhost:5000/api/candidates/export")
        
        print("\n🔑 Credenziali di test:")
        print("   📊 DEVELOPER (accesso completo + gestione utenti):")
        print("      Username: admin")
        print("      Password: admin123")
        print()
        print("   🎤 INTERVISTATORE (accesso standard):")
        print("      Username: interviewer") 
        print("      Password: interview123")
        print()
        print("   👁️ OSPITE (solo visualizzazione candidati + export completo):")
        print("      Username: guest")
        print("      Password: guest123")
        print("      Accesso: Dashboard (con filtri funzionanti), Elenco Candidati, Profilo Candidati")
        print("      Export: Singolo (PDF/CSV/Stampa) e Multiplo (CSV/PDF)")
        print("      Visualizzazione: Immagini, curriculum, grafici statistiche")
        print("      Limitazioni: Non può modificare candidati, punteggi o creare form")
        
        print("\n🚀 Sistema completamente configurato!")

if __name__ == '__main__':
    test_complete_user_system()
