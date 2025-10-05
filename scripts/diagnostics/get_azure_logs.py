#!/usr/bin/env python3
"""
Script per recuperare i log di Azure Web App tramite REST API
"""

import requests
import json
import os
from datetime import datetime, timedelta
import base64

def get_azure_logs():
    """Recupera i log dall'applicazione Azure"""
    
    # Configurazione Azure (da sostituire con i tuoi valori)
    app_name = "flask-w3-prod-app"
    resource_group = "w3-resource-group"  # Sostituisci con il tuo resource group
    subscription_id = "your-subscription-id"  # Sostituisci con il tuo subscription ID
    
    print("🔍 Recupero log da Azure Web App...")
    print(f"📱 App: {app_name}")
    print("=" * 50)
    
    # URL per i log di Azure
    log_url = f"https://{app_name}.scm.azurewebsites.net/api/logs/recent"
    
    # Per ora mostriamo come accedere manualmente ai log
    print("🌐 Per visualizzare i log di Azure Web App:")
    print()
    print("METODO 1 - Portale Azure:")
    print("1. Vai su https://portal.azure.com")
    print("2. Cerca 'flask-w3-prod-app'")
    print("3. Vai su 'Log stream' nel menu laterale")
    print("4. Oppure 'Advanced Tools' > 'Go' > 'Debug console'")
    print()
    print("METODO 2 - URL diretti:")
    print(f"• Log stream: https://{app_name}.scm.azurewebsites.net/api/logstream")
    print(f"• Debug console: https://{app_name}.scm.azurewebsites.net/DebugConsole")
    print(f"• File system: https://{app_name}.scm.azurewebsites.net/api/vfs/LogFiles/")
    print()
    print("METODO 3 - Azure CLI (se installato):")
    print(f"az webapp log tail --name {app_name} --resource-group [RESOURCE_GROUP]")
    print()
    print("METODO 4 - File di log comuni da controllare:")
    print("• /LogFiles/stdout.log")
    print("• /LogFiles/stderr.log")
    print("• /LogFiles/Application/")
    print("• /site/wwwroot/")

def check_common_errors():
    """Controlla errori comuni nelle applicazioni Flask su Azure"""
    print("\n🚨 ERRORI COMUNI DA VERIFICARE:")
    print("=" * 50)
    
    print("1. MIGRAZIONI DATABASE:")
    print("   • Azure non ha eseguito 'flask db upgrade'")
    print("   • Campi del database mancanti (has_children, instagram)")
    print("   • Connessione al database SQL Server fallita")
    print()
    
    print("2. VARIABILI AMBIENTE:")
    print("   • DB_USER, DB_PASSWORD, DB_SERVER, DB_NAME")
    print("   • SECRET_KEY mancante")
    print("   • AZURE_STORAGE_CONNECTION_STRING")
    print()
    
    print("3. DIPENDENZE PYTHON:")
    print("   • pyodbc non installato correttamente")
    print("   • Driver ODBC mancante")
    print("   • Conflitti di versione nei requirements.txt")
    print()
    
    print("4. CONFIGURAZIONE AZURE:")
    print("   • startup.txt non eseguito")
    print("   • Timeout durante l'avvio")
    print("   • Python version mismatch")

def simulate_log_check():
    """Simula il controllo dei log più comuni"""
    print("\n📋 CHECKLIST DIAGNOSTICA:")
    print("=" * 50)
    
    # Controlla se i file locali sono corretti
    files_to_check = [
        "startup.txt",
        "requirements.txt", 
        "app.py",
        "w3form/config.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - Presente")
        else:
            print(f"❌ {file_path} - MANCANTE")
    
    print(f"\n⏰ Ora locale: {datetime.now()}")
    print("📍 Controllare i log di Azure per errori specifici")

if __name__ == '__main__':
    get_azure_logs()
    check_common_errors()
    simulate_log_check()
