#!/usr/bin/env python3
"""
Script per testare la connettività ai servizi Azure e simulare l'ambiente di produzione
"""

import sys
import os
import requests
from datetime import datetime

def test_azure_connectivity():
    """Testa la connettività verso Azure"""
    print("🌐 Test Connettività Azure")
    print("=" * 40)
    
    # Test 1: Connessione all'applicazione
    app_url = "https://flask-w3-prod-app.azurewebsites.net/"
    print(f"🔗 Test connessione a: {app_url}")
    
    try:
        response = requests.get(app_url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📏 Content Length: {len(response.content)} bytes")
        
        if response.status_code == 500:
            print("❌ Internal Server Error - Controllare i log")
            print("🔍 Headers di risposta:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")
        elif response.status_code == 200:
            print("✅ Applicazione raggiungibile")
        else:
            print(f"⚠️  Status inatteso: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - L'applicazione potrebbe essere lenta ad avviarsi")
    except requests.exceptions.ConnectionError:
        print("❌ Errore di connessione - Verificare la rete")
    except Exception as e:
        print(f"❌ Errore generico: {e}")
    
    # Test 2: Endpoint Kudu (management)
    kudu_url = "https://flask-w3-prod-app.scm.azurewebsites.net/"
    print(f"\n🛠️  Test endpoint Kudu: {kudu_url}")
    
    try:
        response = requests.get(kudu_url, timeout=10)
        print(f"📊 Kudu Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Kudu raggiungibile")
        else:
            print("⚠️  Kudu non raggiungibile")
    except Exception as e:
        print(f"❌ Kudu non accessibile: {e}")

def get_log_urls():
    """Restituisce gli URL per accedere ai log"""
    print("\n📋 URL DIRETTI PER I LOG:")
    print("=" * 40)
    
    urls = {
        "Log Stream Live": "https://flask-w3-prod-app.scm.azurewebsites.net/api/logstream",
        "Debug Console": "https://flask-w3-prod-app.scm.azurewebsites.net/DebugConsole",
        "File Explorer": "https://flask-w3-prod-app.scm.azurewebsites.net/api/vfs/",
        "Application Logs": "https://flask-w3-prod-app.scm.azurewebsites.net/api/vfs/LogFiles/Application/",
        "Stdout Logs": "https://flask-w3-prod-app.scm.azurewebsites.net/api/vfs/LogFiles/stdout.log",
        "Site Root": "https://flask-w3-prod-app.scm.azurewebsites.net/api/vfs/site/wwwroot/"
    }
    
    for name, url in urls.items():
        print(f"🔗 {name}:")
        print(f"   {url}")
        print()

def check_deployment_status():
    """Controlla lo stato del deployment"""
    print("📦 STATO DEPLOYMENT:")
    print("=" * 40)
    
    deployment_url = "https://flask-w3-prod-app.scm.azurewebsites.net/api/deployments"
    
    try:
        # Nota: Questo richiede autenticazione, ma proviamo
        response = requests.get(deployment_url, timeout=10)
        if response.status_code == 200:
            print("✅ API Deployment accessibile")
        else:
            print(f"⚠️  API Deployment: Status {response.status_code}")
    except Exception as e:
        print(f"ℹ️  API Deployment: {e}")
    
    print("\n💡 Per controllare i deployment:")
    print("1. Vai su https://portal.azure.com")
    print("2. Cerca 'flask-w3-prod-app'")
    print("3. Sezione 'Deployment' > 'Deployment Center'")

def show_manual_log_access():
    """Mostra come accedere manualmente ai log"""
    print("\n🔧 ACCESSO MANUALE AI LOG:")
    print("=" * 40)
    print("1. Apri: https://portal.azure.com")
    print("2. Cerca: flask-w3-prod-app")
    print("3. Nel menu laterale:")
    print("   • 'Monitoring' > 'Log stream'")
    print("   • 'Development Tools' > 'Advanced Tools' > 'Go'")
    print("   • 'Development Tools' > 'Console'")
    print()
    print("4. Nel Kudu Console, controlla questi file:")
    print("   • D:\\home\\LogFiles\\stdout.log")
    print("   • D:\\home\\LogFiles\\stderr.log") 
    print("   • D:\\home\\LogFiles\\Application\\")
    print("   • D:\\home\\site\\wwwroot\\")

if __name__ == '__main__':
    print(f"🕒 Diagnostica Azure - {datetime.now()}")
    print("=" * 60)
    
    test_azure_connectivity()
    get_log_urls()
    check_deployment_status()
    show_manual_log_access()
    
    print("\n" + "=" * 60)
    print("🎯 PROSSIMI PASSI:")
    print("1. Controlla i log usando gli URL sopra")
    print("2. Verifica le variabili d'ambiente su Azure")
    print("3. Controlla se le migrazioni sono state eseguite")
    print("4. Verifica che tutte le dipendenze siano installate")
