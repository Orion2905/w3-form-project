from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from flask import current_app
from datetime import datetime, timedelta
import os

def upload_to_azure(file_stream, filename):
    connect_str = current_app.config['AZURE_STORAGE_CONNECTION_STRING']
    container = current_app.config['AZURE_STORAGE_CONTAINER']
    blob_service = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service.get_blob_client(container=container, blob=filename)
    blob_client.upload_blob(file_stream, overwrite=True)
    return blob_client.url

def generate_secure_url(blob_url, expiry_hours=1):
    """
    Genera un URL sicuro con SAS token per accedere ai file blob
    """
    try:
        # Se blob_url è solo un nome file, costruisci l'URL completo
        if not blob_url.startswith('https://'):
            blob_url = f"https://w3data.blob.core.windows.net/candidati-files/{blob_url}"
        
        # Estrai il nome del blob dall'URL
        blob_name = blob_url.split('/')[-1]
        
        # Configurazione Azure
        connect_str = current_app.config['AZURE_STORAGE_CONNECTION_STRING']
        container = current_app.config['AZURE_STORAGE_CONTAINER']
        
        # Estrai account name e account key dalla connection string
        conn_parts = dict(item.split('=', 1) for item in connect_str.split(';') if '=' in item)
        account_name = conn_parts.get('AccountName')
        account_key = conn_parts.get('AccountKey')
        
        if not account_name or not account_key:
            current_app.logger.error("Account name o account key mancanti dalla connection string")
            return blob_url  # Fallback all'URL originale se non riusciamo a generare SAS
        
        # Genera SAS token
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        # Costruisci URL sicuro
        secure_url = f"https://{account_name}.blob.core.windows.net/{container}/{blob_name}?{sas_token}"
        return secure_url
        
    except Exception as e:
        current_app.logger.error(f"Errore nella generazione SAS URL per {blob_url}: {e}")
        return blob_url  # Fallback all'URL originale

def get_secure_image_url(image_url):
    """
    Ottieni URL sicuro per immagini profilo (scadenza più lunga)
    """
    if not image_url or not image_url.startswith('https://'):
        return None
    return generate_secure_url(image_url, expiry_hours=24)

def get_secure_document_url(document_url, inline=True):
    """
    Ottieni URL sicuro per documenti (scadenza di 3 ore per visualizzazione)
    """
    if not document_url or not document_url.startswith('https://'):
        return None
    
    secure_url = generate_secure_url(document_url, expiry_hours=3)
    
    # Se richiesta visualizzazione inline, aggiungi parametri per iframe
    if inline and secure_url:
        # Aggiungi parametri per forzare visualizzazione inline
        separator = '&' if '?' in secure_url else '?'
        secure_url += f"{separator}inline=1"
    
    return secure_url
