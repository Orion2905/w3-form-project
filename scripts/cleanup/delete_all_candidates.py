#!/usr/bin/env python3
"""
Script per eliminare tutti i candidati dal database insieme alle loro relazioni associate.
ATTENZIONE: Questa operazione è irreversibile!
"""

import sys
import os
from datetime import datetime

# Aggiungi il percorso del progetto al PATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from w3form import db, create_app
from w3form.models import Candidate, Photo, Curriculum, Score, ShareLink
from sqlalchemy import text

def delete_all_candidates():
    """Elimina tutti i candidati e le loro relazioni associate"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️  Iniziando la pulizia del database...")
            print("=" * 50)
            
            # Conta i record prima dell'eliminazione
            candidate_count = Candidate.query.count()
            photo_count = Photo.query.count()
            curriculum_count = Curriculum.query.count()
            score_count = Score.query.count()
            
            print(f"📊 Record trovati:")
            print(f"   • Candidati: {candidate_count}")
            print(f"   • Foto: {photo_count}")
            print(f"   • Curriculum: {curriculum_count}")
            print(f"   • Punteggi: {score_count}")
            print()
            
            if candidate_count == 0:
                print("✅ Nessun candidato trovato nel database.")
                return
            
            # Conferma dall'utente
            confirm = input("⚠️  ATTENZIONE: Questa operazione eliminerà TUTTI i candidati e i dati associati.\n"
                          "Sei sicuro di voler continuare? (scrivi 'ELIMINA' per confermare): ")
            
            if confirm != 'ELIMINA':
                print("❌ Operazione annullata dall'utente.")
                return
            
            print("\n🔄 Eliminazione in corso...")
            
            # L'eliminazione a cascata dovrebbe gestire automaticamente le relazioni,
            # ma per sicurezza eliminiamo esplicitamente nell'ordine corretto
            
            # 1. Elimina i punteggi
            if score_count > 0:
                print("   🗑️  Eliminazione punteggi...")
                Score.query.delete()
                print(f"   ✅ Eliminati {score_count} punteggi")
            
            # 2. Elimina le foto
            if photo_count > 0:
                print("   🗑️  Eliminazione foto...")
                Photo.query.delete()
                print(f"   ✅ Eliminate {photo_count} foto")
            
            # 3. Elimina i curriculum
            if curriculum_count > 0:
                print("   🗑️  Eliminazione curriculum...")
                Curriculum.query.delete()
                print(f"   ✅ Eliminati {curriculum_count} curriculum")
            
            # 4. Elimina i candidati
            print("   🗑️  Eliminazione candidati...")
            Candidate.query.delete()
            print(f"   ✅ Eliminati {candidate_count} candidati")
            
            # Commit delle modifiche
            db.session.commit()
            
            # Reset degli ID auto-incrementali (opzionale)
            print("   🔄 Reset contatori ID...")
            try:
                # Per SQL Server
                db.session.execute(text("DBCC CHECKIDENT ('candidate', RESEED, 0)"))
                db.session.execute(text("DBCC CHECKIDENT ('photo', RESEED, 0)"))
                db.session.execute(text("DBCC CHECKIDENT ('curriculum', RESEED, 0)"))
                db.session.execute(text("DBCC CHECKIDENT ('score', RESEED, 0)"))
                db.session.commit()
                print("   ✅ Contatori ID resettati")
            except Exception as e:
                print(f"   ⚠️  Avviso: Non è stato possibile resettare i contatori ID: {e}")
            
            print()
            print("🎉 Pulizia completata con successo!")
            print("=" * 50)
            print(f"📊 Riepilogo operazione:")
            print(f"   • Data/ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   • Candidati eliminati: {candidate_count}")
            print(f"   • Foto eliminate: {photo_count}")
            print(f"   • Curriculum eliminati: {curriculum_count}")
            print(f"   • Punteggi eliminati: {score_count}")
            print(f"   • Totale record eliminati: {candidate_count + photo_count + curriculum_count + score_count}")
            
        except Exception as e:
            print(f"❌ Errore durante l'eliminazione: {e}")
            db.session.rollback()
            print("🔄 Rollback eseguito. I dati non sono stati modificati.")
            return False
        
        return True

if __name__ == '__main__':
    delete_all_candidates()
