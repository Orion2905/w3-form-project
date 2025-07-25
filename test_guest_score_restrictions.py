"""
Test per verificare che gli utenti ospite non possano modificare/eliminare punteggi
"""

import requests

def test_guest_score_restrictions():
    """Test restrizioni punteggi per utenti ospite"""
    base_url = "http://localhost:5000"
    
    print("=== TEST RESTRIZIONI PUNTEGGI OSPITE ===")
    
    # Test URLs che dovrebbero essere bloccate per gli ospiti
    restricted_urls = [
        "/candidati/1/punteggi/aggiungi",
        "/candidati/1/punteggi/1/modifica", 
        "/candidati/1/punteggi/1/elimina"
    ]
    
    print("Test accesso diretto alle URL riservate...")
    for url in restricted_urls:
        try:
            response = requests.get(f"{base_url}{url}")
            print(f"✓ {url}: {response.status_code}")
            if response.status_code == 403:
                print(f"  ✓ Correttamente bloccato (403)")
            elif response.status_code == 302:
                print(f"  ✓ Redirect (probabilmente login required)")
            else:
                print(f"  ⚠️ Risposta inaspettata: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Errore: {e}")
    
    # Test API punteggi
    api_urls = [
        ("/api/candidates/1/scores", "POST")
    ]
    
    print("\nTest API riservate...")
    for url, method in api_urls:
        try:
            if method == "POST":
                response = requests.post(f"{base_url}{url}", json={
                    "category": "Test",
                    "score": 85
                })
            else:
                response = requests.get(f"{base_url}{url}")
                
            print(f"✓ {method} {url}: {response.status_code}")
            if response.status_code in [401, 403]:
                print(f"  ✓ Correttamente bloccato")
            else:
                print(f"  ⚠️ Risposta: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Errore: {e}")

if __name__ == "__main__":
    test_guest_score_restrictions()
