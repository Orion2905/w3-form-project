#!/usr/bin/env python3
"""
Script di test per verificare le API dei filtri della dashboard
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_api(endpoint, params=None):
    """Testa un endpoint API e stampa i risultati"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items() if v])
        
        print(f"\n🔍 Testing: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🚀 Test delle API dei filtri dashboard")
    print("=" * 50)
    
    # Test API eventi
    print("\n1. TEST API EVENTI")
    eventi = test_api("/api/stats/eventi")
    
    # Test API aziende
    print("\n2. TEST API AZIENDE")
    aziende = test_api("/api/stats/aziende")
    
    # Test API summary senza filtri
    print("\n3. TEST API SUMMARY (senza filtri)")
    summary_all = test_api("/api/stats/summary")
    
    # Test API summary con filtro evento (se esistono eventi)
    if eventi and len(eventi) > 0:
        print(f"\n4. TEST API SUMMARY (filtro evento: {eventi[0]})")
        summary_evento = test_api("/api/stats/summary", {"evento": eventi[0]})
    
    # Test API summary con filtro azienda (se esistono aziende)
    if aziende and len(aziende) > 0:
        print(f"\n5. TEST API SUMMARY (filtro azienda: {aziende[0]})")
        summary_azienda = test_api("/api/stats/summary", {"azienda": aziende[0]})
    
    # Test API gender con filtri
    if eventi and len(eventi) > 0:
        print(f"\n6. TEST API GENDER (filtro evento: {eventi[0]})")
        gender_filtered = test_api("/api/stats/gender", {"evento": eventi[0]})
    
    # Test API roles con filtri
    if aziende and len(aziende) > 0:
        print(f"\n7. TEST API ROLES (filtro azienda: {aziende[0]})")
        roles_filtered = test_api("/api/stats/roles", {"azienda": aziende[0]})
    
    print("\n" + "=" * 50)
    print("🏁 Test completati!")

if __name__ == "__main__":
    main()
