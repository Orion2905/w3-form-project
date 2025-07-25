from w3form import create_app
from w3form.models import db, SystemSettings

app = create_app()

with app.app_context():
    print("=== VERIFICA SYSTEM SETTINGS ===")
    
    try:
        # Verifica se la tabella esiste
        test_setting = SystemSettings.query.filter_by(key='global_form_test_mode').first()
        
        if test_setting:
            print(f"✓ Impostazione trovata: {test_setting.key} = {test_setting.value} (tipo: {test_setting.value_type})")
            current_value = SystemSettings.get_setting('global_form_test_mode', False)
            print(f"✓ Valore recuperato tramite get_setting: {current_value} (tipo Python: {type(current_value)})")
        else:
            print("✗ Impostazione global_form_test_mode NON trovata")
            print("Creazione impostazione...")
            
            new_setting = SystemSettings(
                key='global_form_test_mode',
                value='false',
                value_type='boolean',
                category='system',
                updated_by=1
            )
            db.session.add(new_setting)
            db.session.commit()
            print("✓ Impostazione creata!")
            
    except Exception as e:
        print(f"✗ Errore accesso tabella: {e}")
        print("Tentativo creazione tabella...")
        
        try:
            # Crea tutte le tabelle
            db.create_all()
            print("✓ Tabelle create")
            
            # Crea l'impostazione di default
            new_setting = SystemSettings(
                key='global_form_test_mode',
                value='false',
                value_type='boolean',
                category='system',
                updated_by=1
            )
            db.session.add(new_setting)
            db.session.commit()
            print("✓ Impostazione di default creata!")
            
        except Exception as e2:
            print(f"✗ Errore creazione: {e2}")
    
    # Verifica finale
    try:
        final_value = SystemSettings.get_setting('global_form_test_mode', False)
        print(f"\n=== STATO FINALE ===")
        print(f"Valore modalità test: {final_value}")
        print(f"Tipo: {type(final_value)}")
    except Exception as e:
        print(f"✗ Errore verifica finale: {e}")
