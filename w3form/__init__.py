from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from w3form.config import Config
from flask_migrate import Migrate  # Importa Flask-Migrate
from flask_cors import CORS

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

    # Importa e registra i blueprint
    from w3form.routes import main
    app.register_blueprint(main)
    return app
