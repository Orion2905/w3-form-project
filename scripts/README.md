# Scripts Directory

Questa cartella contiene tutti gli script di utilità per il progetto W3 Form.

## Struttura

### `/setup`
Script per l'inizializzazione e configurazione del sistema:
- `quick_setup.py` - Setup rapido del progetto
- `init_settings.py` - Inizializzazione impostazioni sistema
- `create_admin_user.py` - Creazione utente amministratore
- `create_system_settings.py` - Creazione tabelle impostazioni
- `create_field_config_table.py` - Creazione configurazione campi
- `check_system_settings.py` - Verifica impostazioni sistema
- `debug_settings.py` - Debug configurazioni

### `/migration`
Script per migrazioni e aggiornamenti database:
- `migrate_user_table.py` - Migrazione tabella utenti
- `fix_database_migration.py` - Fix problemi migrazioni
- Altri script di migrazione specifici

### `/test_data`
Script per popolamento dati di test:
- `add_test_candidates.py` - Aggiunta candidati di test
- `add_test_data_fields.py` - Aggiunta dati campi di test
- `add_test_users.py` - Aggiunta utenti di test
- `create_test_sharelink.py` - Creazione link condivisi di test

## Utilizzo

Eseguire gli script dalla root del progetto:

```bash
# Setup iniziale
python scripts/setup/quick_setup.py

# Migrazione database
python scripts/migration/migrate_user_table.py

# Aggiunta dati di test
python scripts/test_data/add_test_candidates.py
```
