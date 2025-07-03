# Script per aggiungere candidati di test al database
from w3form.models import db, Candidate, Photo, Curriculum
from w3form.config import Config
from app import app
from datetime import datetime, date

# Esempi di candidati di test COMPLETI

test_candidates = [
    Candidate(
        first_name="Mario",
        last_name="Rossi",
        gender="M",
        date_of_birth=date(1990, 5, 15),
        place_of_birth="Milano",
        nationality="Italiana",
        marital_status="Celibe",
        height_cm=180,
        weight_kg=75,
        tshirt_size="L",
        shoe_size_eu="43",
        phone_number="3331234567",
        email="mario.rossi@example.com",
        address="Via Roma 1",
        city="Milano",
        postal_code="20100",
        country_of_residence="Italia",
        id_document="Carta identità",
        id_number="AB1234567",
        id_expiry_date=date(2030, 5, 15),
        id_country="Italia",
        license_country="Italia",
        license_number="MI1234567",
        license_category="B",
        license_issue_date=date(2008, 6, 1),
        license_expiry_date=date(2030, 6, 1),
        years_driving_experience=15,
        auto_moto_munito=True,
        occupation="Sviluppatore Python",
        other_experience="Esperienza in sviluppo web e automazione.",
        availability="Immediata",
        other_location="",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Avanzato",
        language_3="Francese",
        proficiency_3="Base",
        created_at=datetime(2024, 6, 1)
    ),
    Candidate(
        first_name="Giulia",
        last_name="Bianchi",
        gender="F",
        date_of_birth=date(1995, 8, 22),
        place_of_birth="Roma",
        nationality="Italiana",
        marital_status="Nubile",
        height_cm=165,
        weight_kg=58,
        tshirt_size="M",
        shoe_size_eu="38",
        phone_number="3339876543",
        email="giulia.bianchi@example.com",
        address="Via Appia 10",
        city="Roma",
        postal_code="00100",
        country_of_residence="Italia",
        id_document="Passaporto",
        id_number="YA9876543",
        id_expiry_date=date(2029, 8, 22),
        id_country="Italia",
        license_country="Italia",
        license_number="RM9876543",
        license_category="B",
        license_issue_date=date(2013, 9, 1),
        license_expiry_date=date(2029, 9, 1),
        years_driving_experience=12,
        auto_moto_munito=True,
        occupation="Data Analyst",
        other_experience="Stage in azienda di consulenza dati.",
        availability="1 settimana",
        other_location="",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Intermedio",
        language_3="Spagnolo",
        proficiency_3="Base",
        created_at=datetime(2024, 6, 2)
    ),
    Candidate(
        first_name="Luca",
        last_name="Verdi",
        gender="M",
        date_of_birth=date(1985, 2, 10),
        place_of_birth="Torino",
        nationality="Italiana",
        marital_status="Sposato",
        height_cm=175,
        weight_kg=80,
        tshirt_size="XL",
        shoe_size_eu="44",
        phone_number="3335551122",
        email="luca.verdi@example.com",
        address="Corso Francia 99",
        city="Torino",
        postal_code="10100",
        country_of_residence="Italia",
        id_document="Carta identità",
        id_number="TO5551122",
        id_expiry_date=date(2028, 2, 10),
        id_country="Italia",
        license_country="Italia",
        license_number="TO9988776",
        license_category="B",
        license_issue_date=date(2003, 3, 1),
        license_expiry_date=date(2028, 3, 1),
        years_driving_experience=21,
        auto_moto_munito=True,
        occupation="Project Manager",
        other_experience="Gestione team e progetti IT.",
        availability="2 settimane",
        other_location="",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Avanzato",
        language_3="Tedesco",
        proficiency_3="Base",
        created_at=datetime(2024, 6, 3)
    ),
]

def add_candidates():
    with app.app_context():
        for c in test_candidates:
            exists = Candidate.query.filter_by(email=c.email).first()
            if not exists:
                db.session.add(c)
                db.session.flush()  # Ottieni l'id del candidato
                # Aggiungi foto profilo placeholder
                photo = Photo(candidate_id=c.id, filename="testfiles/placeholder_profile.jpg")
                db.session.add(photo)
                # Aggiungi curriculum placeholder
                cv = Curriculum(candidate_id=c.id, filename="testfiles/placeholder_cv.pdf")
                db.session.add(cv)
        db.session.commit()
        print(f"Aggiunti {len(test_candidates)} candidati di test (se non già presenti, con foto e CV placeholder).")

if __name__ == "__main__":
    add_candidates()
