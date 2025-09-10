#!/usr/bin/env python3
"""
Test degli endpoint accessibili agli ospiti
Verifica che tutti gli endpoint delle statistiche siano accessibili
"""

import requests
import json

# URL base dell'applicazione
BASE_URL = "http://localhost:5000"

# Credenziali ospite
GUEST_CREDENTIALS = {
    "username": "guest",
    "password": "guest123"
}

def test_guest_access():
    """Testa l'accesso agli endpoint con credenziali ospite"""
    
    # Lista degli endpoint da testare
    endpoints = [
        "/api/stats/eventi",
        "/api/stats/aziende", 
        "/api/stats/summary",
        "/api/stats/roles",
        "/api/stats/gender",
        "/api/stats/languages",
        "/api/stats/license_category",
        "/api/stats/marital_status",
        "/api/stats/tshirt_size",
        "/api/stats/monthly",
        "/api/stats/cities",
        "/api/stats/latest",
        "/api/filter-options"
    ]
    
    # Crea una sessione
    session = requests.Session()
    
    try:
        print("🔐 Login come ospite...")
        login_response = session.post(f"{BASE_URL}/login", data=GUEST_CREDENTIALS)
        
        if login_response.status_code != 200:
            print(f"❌ Login fallito: {login_response.status_code}")
            return
            
        print("✅ Login riuscito come ospite")
        
        print("\n🧪 Test degli endpoint:")
        print("-" * 50)
        
        success_count = 0
        
        for endpoint in endpoints:
            try:
                response = session.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ {endpoint:<30} OK (200) - {len(data) if isinstance(data, (list, dict)) else 'N/A'} items")
                        success_count += 1
                    except:
                        print(f"✅ {endpoint:<30} OK (200) - Risposta non JSON")
                        success_count += 1
                elif response.status_code == 403:
                    print(f"❌ {endpoint:<30} BLOCCATO (403) - Accesso negato")
                elif response.status_code == 401:
                    print(f"❌ {endpoint:<30} NON AUTORIZZATO (401)")
                else:
                    print(f"⚠️  {endpoint:<30} ERRORE ({response.status_code})")
                    
            except Exception as e:
                print(f"💥 {endpoint:<30} ECCEZIONE: {str(e)}")
        
        print("-" * 50)
        print(f"📊 Risultati: {success_count}/{len(endpoints)} endpoint accessibili")
        
        if success_count == len(endpoints):
            print("🎉 Tutti gli endpoint sono accessibili agli ospiti!")
        else:
            print("⚠️  Alcuni endpoint non sono accessibili agli ospiti")
            
    except Exception as e:
        print(f"💥 Errore durante il test: {str(e)}")

if __name__ == "__main__":
    print("🧪 Test Accessibilità Endpoint per Ospiti")
    print("=" * 50)
    test_guest_access()
