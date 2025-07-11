from w3form import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(16), nullable=False)  # tendina: M/F/Altro
    date_of_birth = db.Column(db.Date, nullable=False)
    place_of_birth = db.Column(db.String(64), nullable=False)
    nationality = db.Column(db.String(32), nullable=False)
    marital_status = db.Column(db.String(16), nullable=False)  # tendina: Celibe/Nubile, Sposato/a, etc.
    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Integer)
    tshirt_size = db.Column(db.String(8))  # tendina: S/M/L/XL/XXL
    shoe_size_eu = db.Column(db.String(8))
    phone_number = db.Column(db.String(32))
    email = db.Column(db.String(128))
    address = db.Column(db.String(128))
    city = db.Column(db.String(64))
    postal_code = db.Column(db.String(16))
    country_of_residence = db.Column(db.String(32))
    id_document = db.Column(db.String(32))  # tendina: Carta identità, Passaporto, etc.
    id_number = db.Column(db.String(64))
    id_expiry_date = db.Column(db.Date)
    id_country = db.Column(db.String(32))
    license_country = db.Column(db.String(32))
    license_number = db.Column(db.String(64))
    license_category = db.Column(db.String(16))  # tendina: A/B/C/D/E
    license_issue_date = db.Column(db.Date)
    license_expiry_date = db.Column(db.Date)
    years_driving_experience = db.Column(db.Integer)
    auto_moto_munito = db.Column(db.Boolean)  # tendina: Sì/No
    occupation = db.Column(db.String(64))
    other_experience = db.Column(db.Text)
    availability = db.Column(db.String(64))  # tendina: Immediata, 1 settimana, etc.
    other_location = db.Column(db.String(64))
    language_1 = db.Column(db.String(32))
    proficiency_1 = db.Column(db.String(16))  # tendina: Base/Intermedio/Avanzato/Madrelingua
    language_2 = db.Column(db.String(32))
    proficiency_2 = db.Column(db.String(16))
    language_3 = db.Column(db.String(32))
    proficiency_3 = db.Column(db.String(16))
    come_sei_arrivato = db.Column(db.String(64))  # nuovo campo a tendina personalizzabile
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('dynamic_form.id', ondelete='CASCADE'), nullable=True)

    photos = db.relationship('Photo', back_populates='candidate', cascade="all, delete-orphan")
    curricula = db.relationship('Curriculum', back_populates='candidate', cascade="all, delete-orphan")
    form = db.relationship('DynamicForm', back_populates='candidates')

    def set_password(self, password):
        """Cripta la password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"



# Per la gestione utenti/ruoli puoi aggiungere questi modelli base:

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(16), nullable=False)  # intervistatore/ospite

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(128), nullable=False)
    candidate = db.relationship('Candidate', back_populates='photos')

class Curriculum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(128), nullable=False)
    candidate = db.relationship('Candidate', back_populates='curricula')

class DynamicForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)  # per url univoca
    description = db.Column(db.Text)
    dropdown_options = db.Column(db.JSON, nullable=False, default=dict)  # opzioni menu a tendina per questo form
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    active_from = db.Column(db.DateTime, nullable=True)
    active_until = db.Column(db.DateTime, nullable=True)
    candidates = db.relationship('Candidate', back_populates='form', cascade="all, delete-orphan")



