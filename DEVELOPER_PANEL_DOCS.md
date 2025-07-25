# Pannello Sviluppatore - Documentazione

## Panoramica
Il Pannello Sviluppatore è una sezione specializzata dell'applicazione accessibile esclusivamente agli utenti con ruolo "developer". Consente la gestione di impostazioni globali del sistema e funzionalità avanzate.

## Accesso
- **URL**: `/developer-panel`
- **Permessi richiesti**: Ruolo "developer"
- **Decoratori**: `@login_required` + `@developer_required`

## Funzionalità Principali

### 1. Modalità Test Globale
La modalità test globale sostituisce la modalità test per singolo form, applicandosi a tutti i form dinamici del sistema.

**Caratteristiche:**
- Impostazione globale che influenza tutti i form
- Toggle rapido on/off
- Indicatori visivi quando attiva
- Storico delle modifiche con audit trail

**API Endpoints:**
- `GET /api/developer/settings` - Recupera impostazioni correnti
- `POST /api/developer/settings` - Aggiorna multiple impostazioni
- `POST /api/developer/test-mode/toggle` - Toggle rapido modalità test

### 2. Impostazioni di Sistema
Gestione centralizzata delle configurazioni globali:

**Impostazioni disponibili:**
- `global_form_test_mode`: Modalità test per tutti i form (boolean)
- `system_maintenance_mode`: Modalità manutenzione sistema (boolean)
- `debug_mode`: Modalità debug interfaccia (boolean)

### 3. Informazioni Sistema
Pannello informativo con:
- Versione applicazione
- Data ultimo aggiornamento
- Ambiente di esecuzione
- Lista sviluppatori attivi

## Modello SystemSettings

### Struttura Tabella
```sql
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY,
    key VARCHAR(128) NOT NULL UNIQUE,
    value TEXT NOT NULL,
    value_type VARCHAR(16) DEFAULT 'string',
    category VARCHAR(64) DEFAULT 'general',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES user(id)
);
```

### Metodi Disponibili

**SystemSettings.get_setting(key, default=None)**
- Recupera un valore con conversione automatica del tipo
- Supporta boolean, integer, float, string
- Ritorna default se la chiave non esiste

**SystemSettings.set_setting(key, value, user_id, category='general')**
- Imposta un valore con conversione automatica del tipo
- Aggiorna timestamp e utente modificatore
- Crea nuovo record o aggiorna esistente

### Conversione Tipi Automatica
Il sistema rileva automaticamente il tipo di valore:
- `bool` → `'boolean'`, memorizzato come 'true'/'false'
- `int` → `'integer'`, memorizzato come stringa numerica
- `float` → `'float'`, memorizzato con notazione decimale
- `str` → `'string'`, memorizzato as-is

## Integrazione con DynamicForm

### Metodi Aggiunti
Il modello `DynamicForm` ora include:

**is_test_mode_active()** 
- Verifica se la modalità test globale è attiva
- Utilizza `SystemSettings.get_setting('global_form_test_mode', False)`

**test_mode (property)**
- Proprietà di compatibilità per codice esistente
- Ritorna il valore della modalità test globale

## Sicurezza e Permessi

### Controllo Accessi
- Tutti gli endpoint richiedono `@login_required`
- Pannello e API richiedono `@developer_required`
- Solo utenti developer possono modificare impostazioni globali

### Audit Trail
- Ogni modifica è tracciata con utente e timestamp
- Campo `updated_by` collega alle modifiche dell'utente
- Possibilità di implementare log dettagliato delle modifiche

## Frontend (JavaScript)

### Funzionalità Implementate
- Toggle real-time modalità test con feedback visivo
- Caricamento dinamico impostazioni via AJAX
- Toast notifications per successo/errore
- Sincronizzazione stato UI con backend

### Eventi Gestiti
- Click su switch modalità test
- Click su bottone toggle
- Salvataggio impostazioni multiple
- Ricaricamento impostazioni

## Utilizzo Tipico

### Attivazione Modalità Test
1. Accesso a `/developer-panel`
2. Sezione "Modalità Test Globale"
3. Toggle switch o click bottone "Attiva Test Mode"
4. Conferma con notifica toast
5. Tutti i form ora mostrano indicatori di test

### Gestione Impostazioni
1. Pannello "Impostazioni di Sistema"
2. Modifica toggle per varie opzioni
3. Click "Salva Impostazioni"
4. Conferma aggiornamento

## Estensioni Future

### Impostazioni Aggiuntive Pianificate
- `max_file_upload_size`: Dimensione massima upload
- `session_timeout`: Timeout sessione utenti
- `backup_enabled`: Abilitazione backup automatici
- `notification_email`: Email per notifiche sistema

### Funzionalità Avanzate
- Log delle attività sviluppatore
- Backup/restore configurazioni
- Deploy di aggiornamenti
- Monitoraggio performance sistema

## Note Tecniche

### Requisiti
- SQLAlchemy per gestione database
- Flask-Login per autenticazione
- Bootstrap 5 per interfaccia
- jQuery per interazioni AJAX

### File Coinvolti
- `/w3form/routes.py` - Route pannello e API
- `/w3form/models.py` - Modello SystemSettings
- `/templates/developer_panel.html` - Template principale
- `/templates/layout_sidebar.html` - Link navigazione

### Database Migration
Per sistemi esistenti, eseguire:
```bash
python create_system_settings.py
```

Questo script:
1. Crea la tabella `system_settings`
2. Inizializza valori di default
3. Verifica integrità configurazione
