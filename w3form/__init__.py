from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from w3form.config import Config
from flask_migrate import Migrate  # Importa Flask-Migrate
from flask_cors import CORS
from w3form.azure_utils import get_secure_image_url, get_secure_document_url

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # Inizializza Migrate



def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")  # Percorsi corretti
    
    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app, db)  # Collega Migrate con Flask e SQLAlchemy

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from w3form.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Aggiungi funzioni helper per i template
    @app.template_filter('secure_blob_url')
    def secure_blob_url_filter(blob_url, file_type='document'):
        """
        Filtro template per generare URL sicuri per i blob
        Usage: {{ blob_url|secure_blob_url('image') }}
        """
        if not blob_url:
            return None
        if file_type == 'image':
            return get_secure_image_url(blob_url)
        else:
            return get_secure_document_url(blob_url)

    # Importa e registra i blueprint
    from w3form.routes import main
    app.register_blueprint(main)
    
    from w3form.api_candidates import api as api_candidates
    app.register_blueprint(api_candidates)
    
    from w3form.api_candidates import api_stats
    app.register_blueprint(api_stats)
    
    return app
