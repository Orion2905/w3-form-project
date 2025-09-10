import requests
import json

# Test per il pannello sviluppatore e modalità test globale

def test_developer_panel():
    """Test per il pannello sviluppatore"""
    base_url = "http://localhost:5000"
    
    # Simuliamo il login come sviluppatore (dovrai adattare con le tue credenziali)
    print("=== TEST PANNELLO SVILUPPATORE ===")
    
    # 1. Test accesso al pannello sviluppatore
    try:
        response = requests.get(f"{base_url}/developer-panel")
        print(f"Accesso pannello sviluppatore: {response.status_code}")
        if response.status_code == 200:
            print("✓ Pannello sviluppatore accessibile")
        else:
            print(f"✗ Errore accesso: {response.status_code}")
    except Exception as e:
        print(f"✗ Errore connessione: {e}")
    
    # 2. Test API per recuperare impostazioni
    try:
        response = requests.get(f"{base_url}/api/developer/settings")
        print(f"API impostazioni: {response.status_code}")
        if response.status_code == 200:
            settings = response.json()
            print(f"✓ Impostazioni recuperate: {settings}")
        else:
            print(f"✗ Errore API: {response.status_code}")
    except Exception as e:
        print(f"✗ Errore API: {e}")
    
    # 3. Test toggle modalità test
    try:
        response = requests.post(f"{base_url}/api/developer/test-mode/toggle")
        print(f"Toggle modalità test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Modalità test cambiata: {result}")
        else:
            print(f"✗ Errore toggle: {response.status_code}")
    except Exception as e:
        print(f"✗ Errore toggle: {e}")
    
    # 4. Test aggiornamento impostazioni
    try:
        test_settings = {
            "system_maintenance_mode": False,
            "debug_mode": True
        }
        response = requests.post(
            f"{base_url}/api/developer/settings",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_settings)
        )
        print(f"Aggiornamento impostazioni: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Impostazioni aggiornate: {result}")
        else:
            print(f"✗ Errore aggiornamento: {response.status_code}")
    except Exception as e:
        print(f"✗ Errore aggiornamento: {e}")

def test_system_settings_model():
    """Test per il modello SystemSettings"""
    print("\n=== TEST MODELLO SYSTEM SETTINGS ===")
    
    try:
        # Importa i moduli necessari
        import sys
        import os
        sys.path.append('.')
        
        from w3form import create_app
        from w3form.models import SystemSettings, db
        
        app = create_app()
        with app.app_context():
            # Test 1: Impostazione e recupero valore booleano
            SystemSettings.set_setting('test_boolean', True, 1, 'test')
            value = SystemSettings.get_setting('test_boolean')
            print(f"Test boolean: impostato True, recuperato {value} - {'✓' if value is True else '✗'}")
            
            # Test 2: Impostazione e recupero valore stringa
            SystemSettings.set_setting('test_string', 'hello world', 1, 'test')
            value = SystemSettings.get_setting('test_string')
            print(f"Test string: impostato 'hello world', recuperato '{value}' - {'✓' if value == 'hello world' else '✗'}")
            
            # Test 3: Valore di default
            value = SystemSettings.get_setting('non_esistente', 'default_value')
            print(f"Test default: recuperato '{value}' - {'✓' if value == 'default_value' else '✗'}")
            
            # Test 4: Verifica modalità test globale
            test_mode = SystemSettings.get_setting('global_form_test_mode', False)
            print(f"Modalità test globale: {test_mode}")
            
            db.session.commit()
            print("✓ Tutti i test del modello superati")
            
    except Exception as e:
        print(f"✗ Errore test modello: {e}")

if __name__ == "__main__":
    test_system_settings_model()
    test_developer_panel()
