#!/usr/bin/env python3
"""
Test per creare un nuovo ShareLink con tutti i campi inclusi i nuovi form fields
"""

from w3form import create_app
from w3form.models import ShareLink, db
import secrets
import string

def create_test_sharelink():
    app = create_app()
    with app.app_context():
        # Crea un nuovo ShareLink di test con tutti i campi
        token = ''.join(secrets.choice(string.ascii_letters + string.digits + '-_') for _ in range(43))
        
        test_fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'occupation', 'total_score', 'form_name', 'form_category', 'form_subcategory'
        ]
        
        share_link = ShareLink(
            token=token,
            fields=test_fields,
            scope='all',
            archived=False
        )
        
        db.session.add(share_link)
        db.session.commit()
        
        print(f"✅ Creato ShareLink di test: {share_link.token}")
        print(f"📋 Fields configurati: {share_link.fields}")
        
        # Testa i dati
        candidates_data = share_link.get_candidates_data()
        if candidates_data:
            print(f"👥 Candidati trovati: {len(candidates_data)}")
            
            first_candidate = candidates_data[0]
            print(f"🔍 Chiavi disponibili: {list(first_candidate.keys())}")
            
            # Verifica i nuovi campi
            new_fields = ['total_score', 'form_name', 'form_category', 'form_subcategory']
            
            for field in new_fields:
                if field in first_candidate:
                    value = first_candidate[field]
                    print(f"✅ {field}: {value}")
                else:
                    print(f"❌ {field}: non trovato")
        else:
            print("❌ Nessun candidato trovato")
        
        return share_link.token

if __name__ == "__main__":
    token = create_test_sharelink()
    print(f"\n🔗 Puoi testare il link a: /shared/{token}")
