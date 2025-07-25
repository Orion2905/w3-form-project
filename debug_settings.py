from w3form import create_app
from w3form.models import db, SystemSettings

app = create_app()

with app.app_context():
    print("=== DEBUGGING SYSTEM SETTINGS ===")
    
    # Mostra tutte le impostazioni nel database
    all_settings = SystemSettings.query.all()
    print(f"Totale impostazioni trovate: {len(all_settings)}")
    
    for setting in all_settings:
        print(f"- {setting.setting_key}: '{setting.setting_value}' (tipo: {setting.setting_type})")
        print(f"  Valore convertito: {setting.typed_value} (tipo Python: {type(setting.typed_value)})")
    
    print("\n=== TEST CONVERSIONE ===")
    # Test la conversione per 'false'
    test_value = 'false'
    converted = test_value.lower() in ('true', '1', 'yes', 'on')
    print(f"'{test_value}' -> {converted}")
    
    test_value2 = 'true' 
    converted2 = test_value2.lower() in ('true', '1', 'yes', 'on')
    print(f"'{test_value2}' -> {converted2}")
    
    # Test get_setting
    print("\n=== TEST GET_SETTING ===")
    result = SystemSettings.get_setting('global_form_test_mode', 'NOT_FOUND')
    print(f"get_setting result: {result} (tipo: {type(result)})")
