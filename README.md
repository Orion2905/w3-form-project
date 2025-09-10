# W3 Form Project

Un sistema completo di gestione candidati e form dinamici costruito con Flask.

## 🚀 Struttura del Progetto

```
w3-form-project/
├── app.py                      # Entry point dell'applicazione
├── run_script.py              # Script runner per utilità
├── requirements.txt           # Dipendenze Python
├── pytest.ini                # Configurazione test
├── .gitignore                 # File Git ignore
│
├── w3form/                    # Package principale dell'applicazione
│   ├── __init__.py           # Inizializzazione Flask app
│   ├── models.py             # Modelli database (SQLAlchemy)
│   ├── routes.py             # Route e endpoint API
│   ├── config.py             # Configurazioni applicazione
│   ├── decorators.py         # Decoratori personalizzati
│   ├── feature_flags.py      # Sistema feature flags
│   ├── api_candidates.py     # API per candidati
│   └── azure_utils.py        # Utilità Azure Storage
│
├── templates/                 # Template Jinja2
│   ├── layout_full.html      # Layout completo
│   ├── layout_sidebar.html   # Layout con sidebar
│   ├── dashboard.html        # Dashboard principale
│   ├── dynamic_form_*.html   # Template per form dinamici
│   ├── candidate_*.html      # Template per candidati
│   └── ...
│
├── static/                    # File statici (CSS, JS, immagini)
│   ├── theme.css             # Stili personalizzati
│   ├── uploads/              # File caricati
│   └── testfiles/            # File di test
│
├── migrations/                # Migrazioni database Alembic
│   ├── versions/             # File di migrazione
│   └── ...
│
├── scripts/                   # Script di utilità organizzati
│   ├── README.md             # Documentazione script
│   ├── setup/                # Script di inizializzazione
│   │   ├── quick_setup.py    # Setup rapido del progetto
│   │   ├── create_admin_user.py
│   │   └── ...
│   ├── migration/            # Script di migrazione DB
│   │   ├── migrate_user_table.py
│   │   └── ...
│   └── test_data/            # Script per dati di test
│       ├── add_test_candidates.py
│       └── ...
│
└── tests/                     # Test del progetto
    ├── README.md             # Documentazione test
    ├── __init__.py          # Init package test
    ├── test_complete_system.py
    ├── test_candidates.py
    └── ...
```

## 🛠️ Setup Rapido

### 1. Installazione Dipendenze
```bash
pip install -r requirements.txt
```

### 2. Setup Automatico
```bash
# Setup completo del progetto
python run_script.py setup

# Oppure step-by-step
python scripts/setup/quick_setup.py
python scripts/setup/create_admin_user.py
```

### 3. Dati di Test (Opzionale)
```bash
python run_script.py test-data
```

### 4. Avvio Applicazione
```bash
python app.py
```

## 🧪 Testing

### Eseguire Tutti i Test
```bash
python run_script.py test
# oppure
python -m pytest tests/
```

### Test Specifici
```bash
python -m pytest tests/test_candidates.py -v
python -m pytest tests/test_api.py --cov=w3form
```

## 📚 Funzionalità Principali

### 🔐 Sistema Utenti
- **Ruoli**: Developer, Admin, User, Ospite
- **Autenticazione**: Flask-Login
- **Permessi**: Decoratori personalizzati (@role_required)

### 📋 Form Dinamici
- Creazione form personalizzati
- Campi configurabili
- Validazione automatica
- Export PDF/Excel

### 👥 Gestione Candidati
- Profili completi candidati
- Upload documenti (Azure Storage)
- Sistema punteggi
- Condivisione link sicuri

### 🎛️ Feature Flags
- Controllo funzionalità tramite pannello sviluppatore
- Attivazione/disattivazione feature in tempo reale
- Sistema di cache integrato

### 📊 Dashboard & Reporting
- Dashboard con statistiche
- Export bulk candidati
- Filtri avanzati
- Stampa PDF personalizzata

## 🔧 Utilità Script Runner

Il file `run_script.py` fornisce un'interfaccia unificata per tutti gli script:

```bash
# Mostra tutti i comandi
python run_script.py help

# Setup completo
python run_script.py setup

# Aggiunta dati di test
python run_script.py test-data

# Migrazioni database
python run_script.py migrate

# Esegui test
python run_script.py test
```

## 🗂️ Organizzazione Script

### `/scripts/setup/`
Script per inizializzazione e configurazione:
- Setup database
- Creazione utenti admin
- Configurazione impostazioni sistema

### `/scripts/migration/`
Script per migrazioni e aggiornamenti database:
- Migrazione tabelle
- Fix problemi database
- Aggiornamenti schema

### `/scripts/test_data/`
Script per popolamento dati di test:
- Candidati di esempio
- Utenti di test
- Dati per sviluppo

## 🧪 Testing Framework

### Struttura Test
- **Unit tests**: Componenti individuali
- **Integration tests**: API endpoints
- **System tests**: Workflow completi
- **Database tests**: Modelli e persistenza

### Configurazione pytest.ini
- Markers per categorizzare test
- Configurazioni ottimali
- Path e pattern automatici

## 🚀 Deployment

### Sviluppo
```bash
python app.py  # Debug mode attivo
```

### Produzione
```bash
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### Variabili d'Ambiente
Crea file `.env`:
```
DATABASE_URL=your_database_url
AZURE_STORAGE_CONNECTION_STRING=your_azure_string
SECRET_KEY=your_secret_key
```

## 📝 Note Sviluppo

- **Python 3.11+** richiesto
- **Database**: PostgreSQL/MySQL supportato
- **Storage**: Azure Blob Storage per file
- **Frontend**: Bootstrap 5 + JavaScript vanilla
- **Template Engine**: Jinja2

## 🤝 Contribuire

1. Aggiungi test per nuove feature
2. Usa il sistema feature flags per sviluppo
3. Segui la struttura organizzata delle cartelle
4. Documenta nuovi script in `/scripts/README.md`

---

*Progetto organizzato e strutturato per facilità di sviluppo e manutenzione* 🎯
