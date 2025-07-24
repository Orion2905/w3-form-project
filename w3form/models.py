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
    additional_document = db.Column(db.String(128))  # Documento aggiuntivo come testo libero
    codice_fiscale = db.Column(db.String(16))  # Codice fiscale italiano
    permesso_soggiorno = db.Column(db.String(64))  # Numero permesso di soggiorno
    license_country = db.Column(db.String(32))
    license_number = db.Column(db.String(64))
    license_category = db.Column(db.String(16))  # tendina: A/B/C/D/E
    license_issue_date = db.Column(db.Date)
    license_expiry_date = db.Column(db.Date)
    years_driving_experience = db.Column(db.Integer)
    auto_moto_munito = db.Column(db.Boolean)  # tendina: Sì/No
    occupation = db.Column(db.String(64))
    other_experience = db.Column(db.Text)
    availability_from = db.Column(db.Date)  # Data di disponibilità da
    availability_till = db.Column(db.Date)  # Data di disponibilità fino a
    city_availability = db.Column(db.String(64))  # Città di disponibilità (una o più città)
    language_1 = db.Column(db.String(32))
    proficiency_1 = db.Column(db.String(16))  # tendina: Base/Intermedio/Avanzato/Madrelingua
    language_2 = db.Column(db.String(32))
    proficiency_2 = db.Column(db.String(16))
    language_3 = db.Column(db.String(32))
    proficiency_3 = db.Column(db.String(16))
    come_sei_arrivato = db.Column(db.String(64))  # nuovo campo a tendina personalizzabile
    archived = db.Column(db.Boolean, default=False, nullable=False)  # Campo per archiviazione
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('dynamic_form.id', ondelete='CASCADE'), nullable=True)

    photos = db.relationship('Photo', back_populates='candidate', cascade="all, delete-orphan")
    curricula = db.relationship('Curriculum', back_populates='candidate', cascade="all, delete-orphan")
    scores = db.relationship('Score', back_populates='candidate', cascade="all, delete-orphan")
    form = db.relationship('DynamicForm', back_populates='candidates')

    def set_password(self, password):
        """Cripta la password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
    
    def get_total_score(self):
        """Calcola il punteggio totale del candidato"""
        try:
            if not hasattr(self, 'scores') or not self.scores:
                return 0
            
            total_weighted = sum(score.weighted_score for score in self.scores)
            total_weight = sum(score.weight for score in self.scores)
            
            if total_weight > 0:
                return total_weighted / total_weight
            return 0
        except Exception:
            return 0
    
    def get_average_score(self):
        """Calcola il punteggio medio del candidato"""
        try:
            if not hasattr(self, 'scores') or not self.scores:
                return 0
            
            total_score = sum(score.score for score in self.scores)
            return total_score / len(self.scores)
        except Exception:
            return 0
    
    def get_scores_by_category(self, category):
        """Ottiene i punteggi per una specifica categoria"""
        return [score for score in self.scores if score.category == category]
    
    def get_score_summary(self):
        """Ottiene un riassunto dei punteggi per categoria"""
        summary = {}
        for score in self.scores:
            if score.category not in summary:
                summary[score.category] = {
                    'scores': [],
                    'total': 0,
                    'count': 0,
                    'average': 0
                }
            summary[score.category]['scores'].append(score)
            summary[score.category]['total'] += score.score
            summary[score.category]['count'] += 1
            summary[score.category]['average'] = summary[score.category]['total'] / summary[score.category]['count']
        
        return summary

# Per la gestione utenti/ruoli puoi aggiungere questi modelli base:

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=True)  # Temporaneamente nullable per migrazione
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(16), nullable=False)  # developer/intervistatore/ospite
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_developer(self):
        return self.role == 'developer'
    
    def is_intervistatore(self):
        return self.role == 'intervistatore'
    
    def is_ospite(self):
        return self.role == 'ospite'

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(512), nullable=False)  # Aumentato per supportare URL lunghi di Azure Blob Storage
    candidate = db.relationship('Candidate', back_populates='photos')

class Curriculum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(512), nullable=False)  # Aumentato per supportare URL lunghi di Azure Blob Storage
    candidate = db.relationship('Candidate', back_populates='curricula')

class DynamicForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)  # per url univoca
    description = db.Column(db.Text)
    category = db.Column(db.String(64), nullable=True)  # Categoria del form (es: "Evento")
    subcategory = db.Column(db.String(64), nullable=True)  # Sottocategoria del form (es: "Azienda")
    dropdown_options = db.Column(db.JSON, nullable=False, default=dict)  # opzioni menu a tendina per questo form
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    active_from = db.Column(db.DateTime, nullable=True)
    active_until = db.Column(db.DateTime, nullable=True)
    
    # Configurazione Privacy Policy
    privacy_policy_enabled = db.Column(db.Boolean, default=True, nullable=False)  # Se mostrare il link
    privacy_policy_url = db.Column(db.String(512), nullable=True)  # URL della privacy policy
    privacy_policy_text = db.Column(db.String(256), nullable=True, default="Leggi l'informativa completa sulla privacy")  # Testo del link
    privacy_policy_new_tab = db.Column(db.Boolean, default=True, nullable=False)  # Se aprire in nuova tab
    
    candidates = db.relationship('Candidate', back_populates='form', cascade="all, delete-orphan")

class Score(db.Model):
    """Tabella per gestire i punteggi dei candidati"""
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)  # chi ha dato il punteggio
    
    # Categorie di punteggio
    category = db.Column(db.String(64), nullable=False)  # es: "Intervista", "Competenze Tecniche", "Soft Skills", etc.
    subcategory = db.Column(db.String(64), nullable=True)  # sottocategoria opzionale
    
    # Punteggio
    score = db.Column(db.Numeric(10, 2), nullable=False)  # punteggio numerico
    max_score = db.Column(db.Numeric(10, 2), nullable=False, default=10.0)  # punteggio massimo possibile
    
    # Dettagli aggiuntivi
    notes = db.Column(db.Text, nullable=True)  # note dell'intervistatore
    weight = db.Column(db.Numeric(10, 2), nullable=False, default=1.0)  # peso del punteggio nel calcolo totale
    
    # Metadati
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relazioni
    candidate = db.relationship('Candidate', back_populates='scores')
    evaluator = db.relationship('User', backref='scores_given')
    
    def __repr__(self):
        return f"<Score {self.candidate_id} - {self.category}: {self.score}/{self.max_score}>"
    
    @property
    def percentage(self):
        """Calcola il punteggio come percentuale"""
        if self.max_score > 0:
            return (self.score / self.max_score) * 100
        return 0
    
    @property
    def weighted_score(self):
        """Calcola il punteggio ponderato"""
        return self.score * self.weight


class ScoreCategory(db.Model):
    """Tabella per gestire le categorie di punteggio predefinite"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    max_score = db.Column(db.Numeric(10, 2), nullable=False, default=10.0)
    weight = db.Column(db.Numeric(10, 2), nullable=False, default=1.0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ScoreCategory {self.name}>"



