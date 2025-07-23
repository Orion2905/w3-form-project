#!/usr/bin/env python3
"""
Script per aggiungere dati di test ai campi mancanti
"""

from w3form import create_app, db
from w3form.models import Candidate
import random

app = create_app()

# Dati di esempio per i campi mancanti
AUTO_MOTO_OPTIONS = ['Sì - Auto', 'Sì - Moto', 'Sì - Entrambi', 'No']
LICENSE_CATEGORIES = ['A', 'B', 'C', 'D', 'A1', 'A2', 'B1', 'C1', 'D1', 'BE', 'CE', 'DE']
TSHIRT_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
LANGUAGES = ['Italiano', 'Inglese', 'Francese', 'Tedesco', 'Spagnolo', 'Russo', 'Cinese', 'Arabo', 'Portoghese']

def add_test_data():
    with app.app_context():
        # Prendi tutti i candidati esistenti
        candidates = Candidate.query.all()
        print(f"Trovati {len(candidates)} candidati")
        
        updated_count = 0
        
        for candidate in candidates:
            # Aggiungi auto_moto_munito se mancante
            if not candidate.auto_moto_munito:
                candidate.auto_moto_munito = random.choice(AUTO_MOTO_OPTIONS)
                updated_count += 1
            
            # Aggiungi license_category se mancante
            if not candidate.license_category:
                candidate.license_category = random.choice(LICENSE_CATEGORIES)
                updated_count += 1
            
            # Aggiungi tshirt_size se mancante
            if not candidate.tshirt_size:
                candidate.tshirt_size = random.choice(TSHIRT_SIZES)
                updated_count += 1
            
            # Aggiungi language_1 se mancante
            if not candidate.language_1:
                candidate.language_1 = random.choice(LANGUAGES)
                updated_count += 1
        
        # Salva i cambiamenti
        try:
            db.session.commit()
            print(f"Aggiornati {updated_count} campi per {len(candidates)} candidati")
            
            # Verifica i dati inseriti
            print("\nVerifica dati inseriti:")
            
            auto_moto_values = db.session.query(Candidate.auto_moto_munito).filter(
                Candidate.auto_moto_munito.isnot(None)
            ).distinct().all()
            print(f"auto_moto_munito: {[x[0] for x in auto_moto_values]}")
            
            license_values = db.session.query(Candidate.license_category).filter(
                Candidate.license_category.isnot(None)
            ).distinct().all()
            print(f"license_category: {[x[0] for x in license_values]}")
            
            tshirt_values = db.session.query(Candidate.tshirt_size).filter(
                Candidate.tshirt_size.isnot(None)
            ).distinct().all()
            print(f"tshirt_size: {[x[0] for x in tshirt_values]}")
            
            language_values = db.session.query(Candidate.language_1).filter(
                Candidate.language_1.isnot(None)
            ).distinct().all()
            print(f"language_1: {[x[0] for x in language_values]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Errore durante il salvataggio: {e}")

if __name__ == '__main__':
    add_test_data()
