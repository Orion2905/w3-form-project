from azure.storage.blob import BlobServiceClient
from flask import current_app

def upload_to_azure(file_stream, filename):
    connect_str = current_app.config['AZURE_STORAGE_CONNECTION_STRING']
    container = current_app.config['AZURE_STORAGE_CONTAINER']
    blob_service = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service.get_blob_client(container=container, blob=filename)
    blob_client.upload_blob(file_stream, overwrite=True)
    return blob_client.url
