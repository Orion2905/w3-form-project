#!/usr/bin/env python3
"""
Script per testare la connessione al database
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Configurazione database
DB_USER = os.environ.get("DB_USER", "Datarockers")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Data2025Rockers!")
DB_SERVER = os.environ.get("DB_SERVER", "w3-server.database.windows.net")
DB_NAME = os.environ.get("DB_NAME", "w3-database")
DB_DRIVER = os.environ.get("DB_DRIVER", "SQL Server")

SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/"
    f"{DB_NAME}?driver={DB_DRIVER}&Encrypt=yes&TrustServerCertificate=no"
)

print(f"Tentativo di connessione con URI: {SQLALCHEMY_DATABASE_URI}")

try:
    # Creazione engine
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    
    # Test connessione
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"✅ Connessione riuscita! Risultato test: {row[0]}")
        
        # Test versione SQL Server
        result = connection.execute(text("SELECT @@VERSION"))
        version = result.fetchone()
        print(f"📋 Versione SQL Server: {version[0][:100]}...")

except Exception as e:
    print(f"❌ Errore di connessione: {e}")
    print("\n🔧 Possibili soluzioni:")
    print("1. Verificare che le credenziali siano corrette")
    print("2. Verificare che il server sia raggiungibile")
    print("3. Controllare le impostazioni del firewall")
    print("4. Verificare che il driver ODBC sia installato correttamente")
