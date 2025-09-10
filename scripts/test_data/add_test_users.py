from w3form import create_app, db
from w3form.models import User

app = create_app()

# Esegui in un contesto applicativo
with app.app_context():
    def add_user(username, password, role):
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Creato utente: {username} ({role})")
        else:
            print(f"Utente già esistente: {username}")

    # Aggiungi utenti di test
    add_user("admin", "adminpass", "intervistatore")
    add_user("intervistatore2", "testpass", "intervistatore")
    add_user("ospite", "ospitepass", "ospite")
