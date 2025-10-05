#!/bin/bash
# Azure Web App Startup Script

echo "🚀 Avvio applicazione Azure Web App..."
echo "Data: $(date)"
echo "========================================"

# Attiva l'ambiente virtuale di Azure
if [ -f /home/site/wwwroot/antenv/bin/activate ]; then
    echo "📦 Attivazione ambiente virtuale Azure..."
    source /home/site/wwwroot/antenv/bin/activate
else
    echo "⚠️  Ambiente virtuale Azure non trovato"
fi

# Verifica Python
echo "🐍 Versione Python: $(python --version 2>&1)"

# Installa dipendenze
echo "📋 Installazione dipendenze..."
pip install -r requirements.txt --no-cache-dir

# Variabili di ambiente per Flask
export FLASK_APP=app.py
export FLASK_ENV=production

# Esegui migrazioni database
echo "🗃️  Esecuzione migrazioni database..."
python -m flask db upgrade || {
    echo "❌ Errore durante le migrazioni del database"
    echo "Tentativo di inizializzazione database..."
    python -m flask db init
    python -m flask db migrate -m "Initial migration"
    python -m flask db upgrade
}

# Verifica stato database
echo "🔍 Verifica connessione database..."
python -c "
from w3form import create_app, db
app = create_app()
with app.app_context():
    try:
        result = db.session.execute(db.text('SELECT 1')).scalar()
        print('✅ Database: Connessione OK')
    except Exception as e:
        print(f'❌ Database: Errore connessione - {e}')
"

echo "🌐 Avvio server Gunicorn..."
echo "========================================"

# Avvia l'applicazione con Gunicorn
exec gunicorn --bind=0.0.0.0:$PORT --workers=1 --timeout=120 --preload app:app
