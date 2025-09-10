from w3form import create_app
from w3form.models import db, SystemSettings

app = create_app()

with app.app_context():
    print("=== INIZIALIZZAZIONE SYSTEM SETTINGS ===")
    
    try:
        # Verifica se l'impostazione esiste già
        existing = SystemSettings.query.filter_by(setting_key='global_form_test_mode').first()
        
        if existing:
            print(f"Impostazione esistente trovata: {existing.setting_key} = '{existing.setting_value}' (tipo: {existing.setting_type})")
        else:
            print("Creazione nuova impostazione global_form_test_mode...")
            
            new_setting = SystemSettings(
                setting_key='global_form_test_mode',
                setting_value='false',
                setting_type='boolean',
                category='system',
                description='Modalità test globale per i form dinamici',
                updated_by=1  # Assumendo che esista un utente con ID 1
            )
            db.session.add(new_setting)
            db.session.commit()
            print("✓ Impostazione creata!")
            
        # Test del valore recuperato
        value = SystemSettings.get_setting('global_form_test_mode', False)
        print(f"Valore recuperato: {value} (tipo: {type(value)})")
        
        # Verifica la conversione manuale
        setting = SystemSettings.query.filter_by(setting_key='global_form_test_mode').first()
        if setting:
            print(f"Valore raw: '{setting.setting_value}'")
            print(f"Tipo setting: '{setting.setting_type}'")
            print(f"typed_value: {setting.typed_value} (tipo: {type(setting.typed_value)})")
            
            # Test conversione manuale
            manual_conversion = setting.setting_value.lower() in ('true', '1', 'yes', 'on')
            print(f"Conversione manuale: {manual_conversion}")
            
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()
