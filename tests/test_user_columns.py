#!/usr/bin/env python3
"""
Script per verificare le colonne della tabella User
"""

import pyodbc
import sys
import os

# Aggiungi il percorso del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from w3form.config import Config

def check_user_table_columns():
    """Verifica le colonne esistenti nella tabella User"""
    try:
        # Connessione al database
        conn = pyodbc.connect(Config.SQLALCHEMY_DATABASE_URI.replace('mssql+pyodbc://', 'DRIVER={ODBC Driver 17 for SQL Server};'))
        cursor = conn.cursor()
        
        print("Connessione al database riuscita!")
        
        # Verifica colonne esistenti
        query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'user'
        ORDER BY ORDINAL_POSITION
        """
        
        cursor.execute(query)
        columns = cursor.fetchall()
        
        print("\n=== COLONNE ATTUALI NELLA TABELLA USER ===")
        for col in columns:
            print(f"- {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
        
        # Controlla se le colonne necessarie esistono
        column_names = [col[0].lower() for col in columns]
        required_columns = ['email', 'first_name', 'last_name']
        
        print("\n=== CONTROLLO COLONNE RICHIESTE ===")
        missing_columns = []
        for req_col in required_columns:
            if req_col in column_names:
                print(f"✓ {req_col} - PRESENTE")
            else:
                print(f"✗ {req_col} - MANCANTE")
                missing_columns.append(req_col)
        
        if missing_columns:
            print(f"\n⚠️  COLONNE MANCANTI: {', '.join(missing_columns)}")
            return False
        else:
            print("\n✓ TUTTE LE COLONNE SONO PRESENTI!")
            return True
            
    except Exception as e:
        print(f"Errore durante la verifica: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_user_table_columns()
