#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from w3form import create_app
from w3form.models import db, Candidate, User
from werkzeug.security import generate_password_hash

def test_app():
    app = create_app()
    print(f"App creata: {app}")
    
    with app.app_context():
        try:
            # Test connessione database
            print("Testando connessione al database...")
            result = db.session.execute(db.text("SELECT 1")).scalar()
            print(f"Connessione DB OK: {result}")
            
            # Test query candidati
            print("Testando query candidati...")
            candidates = Candidate.query.all()
            print(f"Candidati trovati: {len(candidates)}")
            
            # Test query utenti
            print("Testando query utenti...")
            users = User.query.all()
            print(f"Utenti trovati: {len(users)}")
            
            # Se non ci sono utenti, creiamo uno di test
            if len(users) == 0:
                print("Creando utente di test...")
                test_user = User(
                    username='admin',
                    email='admin@test.com',
                    role='admin'
                )
                test_user.set_password('admin123')
                db.session.add(test_user)
                db.session.commit()
                print("Utente di test creato")
            
            # Se non ci sono candidati, creiamo uno di test
            if len(candidates) == 0:
                print("Creando candidato di test...")
                test_candidate = Candidate(
                    first_name='Mario',
                    last_name='Rossi',
                    email='mario.rossi@test.com',
                    phone_number='123456789'
                )
                db.session.add(test_candidate)
                db.session.commit()
                print("Candidato di test creato")
                
                # Ricontrolliamo
                candidates = Candidate.query.all()
                print(f"Candidati dopo la creazione: {len(candidates)}")
            
        except Exception as e:
            print(f"Errore: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_app()
