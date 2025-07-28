"""
Test script per verificare che le nuove colonne form_category e form_subcategory 
siano disponibili nell'esportazione
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from w3form.routes import get_available_export_fields

def test_new_export_fields():
    """Test per verificare che i nuovi campi siano presenti nelle opzioni di esportazione"""
    
    with app.app_context():
        print("=== TEST NUOVI CAMPI ESPORTAZIONE ===")
        
        # Ottieni tutti i campi disponibili
        available_fields = get_available_export_fields()
        
        print(f"Sezioni disponibili: {list(available_fields.keys())}")
        
        # Verifica la sezione "Dati Amministrativi"
        admin_fields = available_fields.get('Dati Amministrativi', [])
        print(f"\nCampi in 'Dati Amministrativi': {len(admin_fields)}")
        
        # Lista tutti i campi
        for field in admin_fields:
            print(f"  - {field['name']}: {field['label']} (default: {field['checked']})")
        
        # Verifica che i nuovi campi siano presenti
        field_names = [field['name'] for field in admin_fields]
        
        if 'form_category' in field_names:
            print("\n✅ Campo 'form_category' trovato!")
        else:
            print("\n❌ Campo 'form_category' NON trovato!")
            
        if 'form_subcategory' in field_names:
            print("✅ Campo 'form_subcategory' trovato!")
        else:
            print("❌ Campo 'form_subcategory' NON trovato!")
        
        # Verifica anche che il form_name esistente sia ancora presente
        if 'form_name' in field_names:
            print("✅ Campo 'form_name' ancora presente!")
        else:
            print("❌ Campo 'form_name' mancante!")
        
        print(f"\nTotale campi in Dati Amministrativi: {len(admin_fields)}")
        print("Campo form_category:", 'form_category' in field_names)
        print("Campo form_subcategory:", 'form_subcategory' in field_names)
        print("Campo form_name:", 'form_name' in field_names)
        print("Campo total_score:", 'total_score' in field_names)
        
        return True

if __name__ == "__main__":
    test_new_export_fields()
