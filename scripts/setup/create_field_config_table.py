from w3form import create_app, db
from w3form.models import FormFieldConfiguration

app = create_app()

with app.app_context():
    print("Creazione della tabella FormFieldConfiguration...")
    try:
        # Crea la tabella se non esiste
        db.create_all()
        print("✅ Tabella FormFieldConfiguration creata con successo!")
        
        # Verifica che la tabella sia stata creata
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'form_field_configurations' in tables:
            print("✅ Tabella 'form_field_configurations' confermata nel database")
            
            # Mostra le colonne della tabella
            columns = inspector.get_columns('form_field_configurations')
            print("\n📋 Colonne della tabella:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("❌ Tabella 'form_field_configurations' non trovata")
            
    except Exception as e:
        print(f"❌ Errore nella creazione della tabella: {e}")
