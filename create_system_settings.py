from w3form import create_app
from w3form.models import db, SystemSettings

app = create_app()

with app.app_context():
    # Verifica se la tabella esiste
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("Tabelle esistenti:", tables)
    
    if 'SystemSettings' not in tables and 'system_settings' not in [t.lower() for t in tables]:
        print("Creazione tabella SystemSettings...")
        try:
            # Crea solo la tabella SystemSettings
            SystemSettings.__table__.create(db.engine, checkfirst=True)
            print("Tabella SystemSettings creata con successo!")
            
            # Inizializza le impostazioni di default
            db.session.add(SystemSettings(
                key='global_form_test_mode',
                value='false',
                value_type='boolean',
                category='system',
                updated_by=1  # Assumiamo che esista un utente con ID 1
            ))
            
            db.session.add(SystemSettings(
                key='system_maintenance_mode',
                value='false',
                value_type='boolean',
                category='system',
                updated_by=1
            ))
            
            db.session.add(SystemSettings(
                key='debug_mode',
                value='false',
                value_type='boolean',
                category='system',
                updated_by=1
            ))
            
            db.session.commit()
            print("Impostazioni di default inizializzate!")
            
        except Exception as e:
            print(f"Errore nella creazione: {e}")
            db.session.rollback()
    else:
        print("La tabella SystemSettings esiste già.")
        
        # Verifica se le impostazioni di default esistono
        test_mode_setting = SystemSettings.query.filter_by(key='global_form_test_mode').first()
        if not test_mode_setting:
            print("Aggiunta impostazioni mancanti...")
            try:
                db.session.add(SystemSettings(
                    key='global_form_test_mode',
                    value='false',
                    value_type='boolean',
                    category='system',
                    updated_by=1
                ))
                db.session.commit()
                print("Impostazione global_form_test_mode aggiunta!")
            except Exception as e:
                print(f"Errore: {e}")
                db.session.rollback()
