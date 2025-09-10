import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from w3form import create_app, db

app = create_app()

with app.app_context():
    print("🔧 Creazione tabella FormFieldConfiguration...")
    try:
        # Crea tutte le tabelle che non esistono
        db.create_all()
        print("✅ Operazione completata!")
        
        # Verifica che la tabella sia stata creata
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'form_field_configurations' in tables:
            print("✅ Tabella 'form_field_configurations' creata con successo")
            
            # Mostra le colonne
            columns = inspector.get_columns('form_field_configurations')
            print("\n📋 Colonne della tabella:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
                
            # Mostra le foreign keys
            foreign_keys = inspector.get_foreign_keys('form_field_configurations')
            if foreign_keys:
                print("\n🔗 Foreign Keys:")
                for fk in foreign_keys:
                    print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        else:
            print("❌ Tabella non trovata")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
