#!/usr/bin/env python3
"""
Script semplificato per aggiungere colonne alla tabella User
"""

import pyodbc
import sys
import os

# Aggiungi il percorso del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_missing_columns():
    """Aggiunge le colonne mancanti alla tabella User"""
    
    # Stringa di connessione per Azure SQL Server
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=w3-server.database.windows.net,1433;"
        "DATABASE=w3-database;"
        "UID=Datarockers;"
        "PWD=Data2025Rockers!;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )
    
    try:
        print("Connessione al database...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print("✓ Connessione riuscita!")
        
        # SQL per aggiungere le colonne mancanti
        alter_commands = [
            "ALTER TABLE [user] ADD email NVARCHAR(100) NULL",
            "ALTER TABLE [user] ADD first_name NVARCHAR(50) NULL", 
            "ALTER TABLE [user] ADD last_name NVARCHAR(50) NULL"
        ]
        
        for command in alter_commands:
            try:
                print(f"Eseguendo: {command}")
                cursor.execute(command)
                conn.commit()
                print("✓ Comando eseguito con successo!")
            except pyodbc.Error as e:
                if "already exists" in str(e) or "Duplicate column name" in str(e):
                    print(f"⚠️  Colonna già esistente: {e}")
                else:
                    print(f"✗ Errore nell'esecuzione: {e}")
                    # Continua con le altre colonne anche se una fallisce
                    
        # Verifica le colonne finali
        print("\n=== VERIFICA COLONNE FINALI ===")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'user'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col[0]} ({col[1]}) - Nullable: {col[2]}")
            
        print("\n✓ Migrazione completata!")
        
    except Exception as e:
        print(f"✗ Errore durante la migrazione: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("Connessione chiusa.")
    
    return True

if __name__ == "__main__":
    add_missing_columns()
