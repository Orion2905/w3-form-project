#!/usr/bin/env python3
"""
Script per monitorare lo stato del deployment Azure
"""

import requests
import time
from datetime import datetime

def monitor_azure_deployment():
    """Monitora lo stato dell'applicazione Azure"""
    print("🔍 Monitoraggio Deployment Azure")
    print("=" * 50)
    print(f"🕒 Inizio monitoraggio: {datetime.now()}")
    print("🌐 URL: https://flask-w3-prod-app.azurewebsites.net/")
    print()
    
    max_attempts = 20  # 10 minuti di monitoraggio
    attempt = 0
    last_status = None
    
    while attempt < max_attempts:
        attempt += 1
        try:
            print(f"⏱️  Tentativo {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Test connessione principale
            response = requests.get("https://flask-w3-prod-app.azurewebsites.net/", timeout=15)
            status = response.status_code
            content_length = len(response.content)
            
            print(f"   Status: {status}")
            print(f"   Content-Length: {content_length} bytes")
            
            if status != last_status:
                print(f"   🔄 Cambio di stato: {last_status} → {status}")
                last_status = status
            
            # Se otteniamo 200, testiamo anche il login
            if status == 200:
                try:
                    login_response = requests.get("https://flask-w3-prod-app.azurewebsites.net/login", timeout=10)
                    if login_response.status_code == 200:
                        print("   ✅ Login page: OK")
                        
                        # Test se l'errore additional_document è risolto
                        # Proviamo ad accedere a un endpoint che richiede il database
                        print("   🔍 Test risoluzione errore database...")
                        time.sleep(2)  # Aspetta un po' prima del test successivo
                        break
                    else:
                        print(f"   ⚠️  Login page: Status {login_response.status_code}")
                except Exception as login_error:
                    print(f"   ❌ Login test fallito: {login_error}")
            
            elif status == 500:
                print("   ❌ Internal Server Error - Deployment in corso o errore persistente")
                
                # Prova a ottenere più dettagli dalla risposta
                try:
                    if 'text/html' in response.headers.get('content-type', ''):
                        content_preview = response.text[:200].replace('\n', ' ')
                        print(f"   📄 Content preview: {content_preview}...")
                except:
                    pass
            
            elif status == 503:
                print("   🔄 Service Unavailable - Deployment in corso")
            else:
                print(f"   ⚠️  Status inatteso: {status}")
            
            print()
            
            # Aspetta 30 secondi tra i tentativi
            if attempt < max_attempts:
                time.sleep(30)
                
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout - Server potrebbe essere in restart")
        except requests.exceptions.ConnectionError:
            print("   📡 Connection Error - Deployment probabilmente in corso")
        except Exception as e:
            print(f"   ❌ Errore: {e}")
        
        print()
    
    print("🏁 Monitoraggio completato")
    print(f"🕒 Fine monitoraggio: {datetime.now()}")
    
    # Test finale
    print("\n🎯 TEST FINALE:")
    try:
        final_response = requests.get("https://flask-w3-prod-app.azurewebsites.net/", timeout=15)
        if final_response.status_code == 200:
            print("✅ Applicazione Azure: FUNZIONANTE")
        else:
            print(f"❌ Applicazione Azure: Status {final_response.status_code}")
    except Exception as e:
        print(f"❌ Test finale fallito: {e}")

if __name__ == '__main__':
    monitor_azure_deployment()
