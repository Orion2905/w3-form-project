from w3form import create_app
from w3form.models import db, Candidate

app = create_app()
with app.app_context():
    try:
        candidates = Candidate.query.all()
        print(f'Numero di candidati trovati: {len(candidates)}')
        if candidates:
            for c in candidates[:5]:
                print(f'ID: {c.id}, Nome: {c.first_name} {c.last_name}, Email: {c.email}')
        else:
            print('Nessun candidato trovato nel database')
    except Exception as e:
        print(f'Errore nella query: {e}')
        import traceback
        traceback.print_exc()
