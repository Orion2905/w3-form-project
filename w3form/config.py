import os
from sqlalchemy.pool import QueuePool

class Config:
    DB_USER = os.environ.get("DB_USER", "Datarockers")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "Data2025Rockers!")
    DB_SERVER = os.environ.get("DB_SERVER", "w3-server.database.windows.net")
    DB_NAME = os.environ.get("DB_NAME", "w3-database")
    DB_DRIVER = "ODBC+Driver+18+for+SQL+Server"
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/"
        f"{DB_NAME}?driver={DB_DRIVER}&Encrypt=yes&TrustServerCertificate=no"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'scegli-una-chiave-sicura')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 1800,
        "pool_timeout": 30,
        "poolclass": QueuePool,
        "echo": False,
        "future": True
    }

    AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
        'AZURE_STORAGE_CONNECTION_STRING',
        'DefaultEndpointsProtocol=https;AccountName=w3data;AccountKey=hht3XfrXMWusuG5RpK+hRF4IyoQQwJtnFbRLMjHzrgxLPKK/0VCoKb3ovGyfTrcMqGt5gzikBuvq+AStL0G08Q==;EndpointSuffix=core.windows.net'
    )
    AZURE_STORAGE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER', 'candidati-files')