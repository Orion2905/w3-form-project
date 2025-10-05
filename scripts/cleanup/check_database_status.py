#!/usr/bin/env python3
"""
Script per verificare lo stato del database - conta i record nelle tabelle principali
"""

import sys
import os
from datetime import datetime

# Aggiungi il percorso del progetto al PATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from w3form import create_app
from w3form.models import Candidate, Photo, Curriculum, Score, DynamicForm, User, ShareLink

def check_database_status():
    """Verifica lo stato del database"""
    app = create_app()
    
    with app.app_context():
        print("📊 Stato del Database")
        print("=" * 40)
        print(f"🕒 Data/ora controllo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Tabelle principali candidati
        print("👥 TABELLE CANDIDATI:")
        print(f"   • Candidati: {Candidate.query.count():>6}")
        print(f"   • Foto: {Photo.query.count():>11}")
        print(f"   • Curriculum: {Curriculum.query.count():>5}")
        print(f"   • Punteggi: {Score.query.count():>7}")
        
        # Tabelle sistema
        print("\n⚙️  TABELLE SISTEMA:")
        print(f"   • Utenti: {User.query.count():>9}")
        print(f"   • Form dinamici: {DynamicForm.query.count():>2}")
        print(f"   • Link condivisi: {ShareLink.query.count():>1}")
        
        print("\n" + "=" * 40)
        
        # Verifica se il database è pulito per i candidati
        total_candidate_data = (Candidate.query.count() + Photo.query.count() + 
                              Curriculum.query.count() + Score.query.count())
        
        if total_candidate_data == 0:
            print("✅ Database candidati: PULITO")
        else:
            print(f"📝 Database candidati: {total_candidate_data} record presenti")

if __name__ == '__main__':
    check_database_status()
