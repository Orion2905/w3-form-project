# Tests Directory

Questa cartella contiene tutti i test per il progetto W3 Form.

## File di Test

### Test di Sistema
- `test_complete_system.py` - Test completo del sistema
- `test_app.py` - Test dell'applicazione principale

### Test Database
- `test_db_connection.py` - Test connessione database
- `test_table_creation.py` - Test creazione tabelle
- `test_candidates.py` - Test modello candidati

### Test API
- `test_filters_api.py` - Test API filtri
- `test_ospite_endpoints.py` - Test endpoint ospite
- `test_developer_panel.py` - Test pannello sviluppatore

### Test Utenti
- `test_user_system.py` - Test sistema utenti
- `test_user_creation.py` - Test creazione utenti
- `test_user_columns.py` - Test colonne utente
- `test_guest_score_restrictions.py` - Test restrizioni punteggi ospite

### Test Funzionalità
- `test_share_fields.py` - Test campi condivisione
- `test_new_export_fields.py` - Test nuovi campi export

## Esecuzione Test

```bash
# Esegui tutti i test
python -m pytest tests/

# Esegui un test specifico
python -m pytest tests/test_complete_system.py

# Esegui con coverage
python -m pytest tests/ --cov=w3form --cov-report=html

# Esegui test verbose
python -m pytest tests/ -v
```

## Requisiti

Per eseguire i test assicurati di avere installato:
```bash
pip install pytest pytest-cov
```
