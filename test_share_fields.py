#!/usr/bin/env python3
"""
Test per verificare che i nuovi campi form vengano inclusi correttamente
nella condivisione candidati.
"""

from w3form import create_app
from w3form.models import ShareLink, Candidate

def test_share_fields():
    app = create_app()
    with app.app_context():
        # Testa con un link di condivisione esistente
        share_link = ShareLink.query.first()
        if not share_link:
            print("❌ Nessun ShareLink trovato nel database")
            return
        
        print(f"✅ Testing ShareLink: {share_link.token}")
        print(f"📋 Fields configurati: {share_link.fields}")
        
        # Ottieni i dati dei candidati
        candidates_data = share_link.get_candidates_data()
        if not candidates_data:
            print("❌ Nessun candidato restituito")
            return
        
        print(f"👥 Candidati trovati: {len(candidates_data)}")
        
        # Testa il primo candidato
        first_candidate = candidates_data[0]
        print(f"🔍 Chiavi disponibili nel primo candidato: {list(first_candidate.keys())}")
        
        # Verifica i nuovi campi
        new_fields = ['total_score', 'form_name', 'form_category', 'form_subcategory']
        
        for field in new_fields:
            if field in share_link.fields:
                if field in first_candidate:
                    value = first_candidate[field]
                    print(f"✅ {field}: {value} (tipo: {type(value).__name__})")
                else:
                    print(f"❌ {field}: non trovato nei dati candidato")
            else:
                print(f"⏭️ {field}: non configurato in questo ShareLink")
        
        # Mostra un esempio di candidato completo
        print("\n📄 Esempio di candidato completo:")
        for key, value in first_candidate.items():
            print(f"   {key}: {value}")

if __name__ == "__main__":
    test_share_fields()
