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
    
    def is_test_mode_active(self):
        """Verifica se la modalità test è attiva globalmente"""
        test_mode_raw = SystemSettings.get_setting('global_form_test_mode', False)
        
        # Conversione esplicita a booleano per gestire stringhe dal database
        if isinstance(test_mode_raw, str):
            return test_mode_raw.lower() in ('true', '1', 'yes', 'on')
        else:
            return bool(test_mode_raw)
    
    @property
    def test_mode(self):
        """Proprietà per compatibilità - usa la modalità test globale"""
        return self.is_test_mode_active()

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

class SystemSettings(db.Model):
    """Tabella per le impostazioni globali del sistema"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(64), unique=True, nullable=False)  # Chiave dell'impostazione
    setting_value = db.Column(db.String(256), nullable=True)  # Valore come stringa
    setting_type = db.Column(db.String(16), nullable=False, default='string')  # tipo: string, boolean, integer, float
    description = db.Column(db.Text, nullable=True)  # Descrizione dell'impostazione
    category = db.Column(db.String(32), nullable=True)  # Categoria per raggruppare le impostazioni
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Chi ha modificato l'impostazione
    
    # Relazione con User
    updated_by_user = db.relationship('User', backref='system_settings_updated')
    
    @property
    def typed_value(self):
        """Restituisce il valore convertito nel tipo corretto"""
        if self.setting_value is None:
            return None
        
        if self.setting_type == 'boolean':
            # Gestisce vari formati per boolean
            if isinstance(self.setting_value, bool):
                return self.setting_value
            if isinstance(self.setting_value, str):
                return self.setting_value.lower() in ('true', '1', 'yes', 'on', 't', 'y')
            return bool(self.setting_value)
        elif self.setting_type == 'integer':
            try:
                return int(self.setting_value)
            except (ValueError, TypeError):
                return None
        elif self.setting_type == 'float':
            try:
                return float(self.setting_value)
            except (ValueError, TypeError):
                return None
        else:
            return self.setting_value
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Ottiene un'impostazione per chiave"""
        setting = cls.query.filter_by(setting_key=key).first()
        if setting:
            return setting.typed_value
        return default
    
    @classmethod
    def set_setting(cls, key, value, setting_type='string', description=None, category=None, user_id=None):
        """Imposta un'impostazione"""
        setting = cls.query.filter_by(setting_key=key).first()
        if not setting:
            setting = cls(setting_key=key)
            db.session.add(setting)
        
        setting.setting_value = str(value) if value is not None else None
        setting.setting_type = setting_type
        if description:
            setting.description = description
        if category:
            setting.category = category
        if user_id:
            setting.updated_by = user_id
        
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f"<SystemSettings {self.setting_key}={self.setting_value}>"


class FormFieldConfiguration(db.Model):
    """
    Configurazione dei campi del form dinamico.
    Permette di controllare visibilità e obbligatorietà per ogni form.
    """
    __tablename__ = 'form_field_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('dynamic_form.id'), nullable=False)
    field_name = db.Column(db.String(128), nullable=False)  # Nome del campo (es: 'first_name', 'email')
    is_visible = db.Column(db.Boolean, default=True, nullable=False)  # Campo visibile o nascosto
    is_required = db.Column(db.Boolean, default=True, nullable=False)  # Campo obbligatorio o facoltativo
    field_order = db.Column(db.Integer, default=0)  # Ordine del campo nel form
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Chi ha modificato la configurazione
    
    # Relazioni
    form = db.relationship('DynamicForm', backref='field_configurations')
    updated_by_user = db.relationship('User', foreign_keys=[updated_by])
    
    # Constraint per evitare duplicati
    __table_args__ = (
        UniqueConstraint('form_id', 'field_name', name='unique_form_field_config'),
    )
    
    @staticmethod
    def get_field_config(form_id, field_name):
        """Ottiene la configurazione di un campo specifico"""
        return FormFieldConfiguration.query.filter_by(
            form_id=form_id, 
            field_name=field_name
        ).first()
    
    @staticmethod
    def set_field_config(form_id, field_name, is_visible=True, is_required=True, user_id=None):
        """Imposta o aggiorna la configurazione di un campo"""
        config = FormFieldConfiguration.get_field_config(form_id, field_name)
        
        if not config:
            config = FormFieldConfiguration(
                form_id=form_id,
                field_name=field_name,
                is_visible=is_visible,
                is_required=is_required,
                updated_by=user_id
            )
            db.session.add(config)
        else:
            config.is_visible = is_visible
            config.is_required = is_required
            config.updated_at = datetime.utcnow()
            if user_id:
                config.updated_by = user_id
        
        db.session.commit()
        return config
    
    @staticmethod
    def get_form_configuration(form_id):
        """Ottiene tutte le configurazioni dei campi per un form"""
        configs = FormFieldConfiguration.query.filter_by(form_id=form_id).all()
        return {config.field_name: config for config in configs}
    
    @staticmethod
    def get_default_fields():
        """Restituisce la lista dei campi predefiniti del form candidato"""
        return {
            # Step 1: Dati anagrafici
            'first_name': {'label': 'Nome', 'step': 1, 'section': 'Informazioni Personali'},
            'last_name': {'label': 'Cognome', 'step': 1, 'section': 'Informazioni Personali'},
            'gender': {'label': 'Genere', 'step': 1, 'section': 'Informazioni Personali'},
            'date_of_birth': {'label': 'Data di Nascita', 'step': 1, 'section': 'Informazioni Personali'},
            'place_of_birth': {'label': 'Luogo di Nascita', 'step': 1, 'section': 'Informazioni Personali'},
            'nationality': {'label': 'Nazionalità', 'step': 1, 'section': 'Informazioni Personali'},
            'marital_status': {'label': 'Stato Civile', 'step': 1, 'section': 'Stato Civile e Contatti'},
            'phone_number': {'label': 'Numero di Telefono', 'step': 1, 'section': 'Stato Civile e Contatti'},
            'email': {'label': 'Indirizzo Email', 'step': 1, 'section': 'Stato Civile e Contatti'},
            'come_sei_arrivato': {'label': 'Come sei arrivato a noi', 'step': 1, 'section': 'Stato Civile e Contatti'},
            'height_cm': {'label': 'Altezza (cm)', 'step': 1, 'section': 'Caratteristiche Fisiche'},
            'weight_kg': {'label': 'Peso (kg)', 'step': 1, 'section': 'Caratteristiche Fisiche'},
            'tshirt_size': {'label': 'Taglia T-shirt', 'step': 1, 'section': 'Caratteristiche Fisiche'},
            'shoe_size_eu': {'label': 'Numero Scarpe (EU)', 'step': 1, 'section': 'Caratteristiche Fisiche'},
            'profile_photo': {'label': 'Immagine Profilo', 'step': 1, 'section': 'Foto Profilo'},
            
            # Step 2: Documenti e patente
            'address': {'label': 'Indirizzo', 'step': 2, 'section': 'Informazioni di Residenza'},
            'city': {'label': 'Città', 'step': 2, 'section': 'Informazioni di Residenza'},
            'postal_code': {'label': 'Codice Postale', 'step': 2, 'section': 'Informazioni di Residenza'},
            'country_of_residence': {'label': 'Paese di Residenza', 'step': 2, 'section': 'Informazioni di Residenza'},
            'id_document': {'label': 'Tipo Documento', 'step': 2, 'section': 'Documento d\'Identità'},
            'id_number': {'label': 'Numero Documento', 'step': 2, 'section': 'Documento d\'Identità'},
            'id_expiry_date': {'label': 'Scadenza Documento', 'step': 2, 'section': 'Documento d\'Identità'},
            'id_country': {'label': 'Paese Documento', 'step': 2, 'section': 'Documento d\'Identità'},
            'additional_document': {'label': 'Documento Aggiuntivo', 'step': 2, 'section': 'Documento d\'Identità'},
            'codice_fiscale': {'label': 'Codice Fiscale', 'step': 2, 'section': 'Documenti Fiscali e Legali'},
            'permesso_soggiorno': {'label': 'Numero Permesso di Soggiorno', 'step': 2, 'section': 'Documenti Fiscali e Legali'},
            'license_country': {'label': 'Paese Patente', 'step': 2, 'section': 'Patente di Guida'},
            'license_number': {'label': 'Numero Patente', 'step': 2, 'section': 'Patente di Guida'},
            'license_category': {'label': 'Categoria Patente', 'step': 2, 'section': 'Patente di Guida'},
            'license_issue_date': {'label': 'Data Rilascio Patente', 'step': 2, 'section': 'Patente di Guida'},
            'license_expiry_date': {'label': 'Scadenza Patente', 'step': 2, 'section': 'Patente di Guida'},
            'years_driving_experience': {'label': 'Anni di Esperienza di Guida', 'step': 2, 'section': 'Esperienza di Guida'},
            'auto_moto_munito': {'label': 'Auto/Moto Munito', 'step': 2, 'section': 'Esperienza di Guida'},
            'curriculum_file': {'label': 'Curriculum', 'step': 2, 'section': 'Upload Curriculum'},
            
            # Step 3: Esperienze e lingue
            'occupation': {'label': 'Occupazione', 'step': 3, 'section': 'Esperienza Lavorativa'},
            'other_experience': {'label': 'Altre Esperienze', 'step': 3, 'section': 'Esperienza Lavorativa'},
            'availability_from': {'label': 'Disponibilità Da', 'step': 3, 'section': 'Disponibilità Lavorativa'},
            'availability_till': {'label': 'Disponibilità Fino A', 'step': 3, 'section': 'Disponibilità Lavorativa'},
            'other_location': {'label': 'Città di Disponibilità', 'step': 3, 'section': 'Disponibilità Lavorativa'},
            'language_1': {'label': 'Prima Lingua', 'step': 3, 'section': 'Competenze Linguistiche'},
            'proficiency_1': {'label': 'Livello Prima Lingua', 'step': 3, 'section': 'Competenze Linguistiche'},
            'language_2': {'label': 'Seconda Lingua', 'step': 3, 'section': 'Competenze Linguistiche'},
            'proficiency_2': {'label': 'Livello Seconda Lingua', 'step': 3, 'section': 'Competenze Linguistiche'},
            'language_3': {'label': 'Terza Lingua', 'step': 3, 'section': 'Competenze Linguistiche'},
            'proficiency_3': {'label': 'Livello Terza Lingua', 'step': 3, 'section': 'Competenze Linguistiche'},
            'gdpr_consent': {'label': 'Consenso al trattamento dei dati personali', 'step': 3, 'section': 'Consenso Privacy'},
        }
    
    def __repr__(self):
        return f"<FormFieldConfiguration form_id={self.form_id} field={self.field_name} visible={self.is_visible} required={self.is_required}>"


class ShareLink(db.Model):
    """
    Modello per gestire i link di condivisione delle liste candidati
    """
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, default='Lista Candidati Condivisa')
    
    # Configurazione dati
    fields = db.Column(db.JSON, nullable=False)  # Lista dei campi da mostrare
    filters = db.Column(db.JSON, nullable=True)  # Filtri applicati (se scope='filtered')
    scope = db.Column(db.String(20), nullable=False, default='all')  # 'all' o 'filtered'
    archived = db.Column(db.Boolean, nullable=False, default=False)  # Se include candidati archiviati
    
    # Sicurezza
    password_hash = db.Column(db.String(255), nullable=True)  # Password opzionale
    
    # Scadenza
    expires_at = db.Column(db.DateTime, nullable=True)  # Data di scadenza opzionale
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    accessed_count = db.Column(db.Integer, default=0, nullable=False)
    last_accessed_at = db.Column(db.DateTime, nullable=True)
    
    # Chi ha creato il link
    created_by = db.Column(db.String(100), nullable=True)  # Email o username del creatore
    
    def set_password(self, password):
        """Imposta la password per il link condiviso"""
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = None
    
    def check_password(self, password):
        """Verifica la password del link condiviso"""
        if not self.password_hash:
            return True  # Nessuna password richiesta
        return check_password_hash(self.password_hash, password)
    
    def is_expired(self):
        """Controlla se il link è scaduto"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_accessible(self):
        """Controlla se il link è ancora accessibile"""
        return not self.is_expired()
    
    def increment_access_count(self):
        """Incrementa il contatore degli accessi"""
        self.accessed_count += 1
        self.last_accessed_at = datetime.utcnow()
        db.session.commit()
    
    def get_candidates_data(self):
        """
        Recupera i dati dei candidati secondo i filtri e campi specificati
        """
        from .models import Candidate, DynamicForm  # Import locale per evitare riferimenti circolari
        from w3form.azure_utils import get_secure_image_url
        from datetime import datetime, date
        from sqlalchemy import or_
        
        # Query base
        query = Candidate.query
        
        # Filtro archiviati
        query = query.filter(Candidate.archived == self.archived)
        
        # Variabile per filtri post-query
        score_ranges_to_filter = None
        
        # Applica filtri se scope è 'filtered'
        if self.scope == 'filtered' and self.filters:
            print(f"DEBUG: Applicando filtri: {self.filters}")  # Debug
            
            # Verifica se abbiamo bisogno del JOIN con DynamicForm
            form_filters = ['form_name', 'form_category', 'form_subcategory']
            needs_form_join = any(filter_key in form_filters for filter_key in self.filters.keys())
            
            if needs_form_join:
                query = query.join(DynamicForm, Candidate.form_id == DynamicForm.id)
            
            for filter_key, filter_value in self.filters.items():
                if not filter_value:
                    continue
                    
                # Gestione ricerca globale
                if filter_key == 'search':
                    search_term = f'%{filter_value}%'
                    search_conditions = []
                    # Cerca in tutti i campi stringa principali
                    string_fields = ['first_name', 'last_name', 'email', 'phone_number', 'city', 
                                   'nationality', 'occupation', 'come_sei_arrivato']
                    for field in string_fields:
                        if hasattr(Candidate, field):
                            column = getattr(Candidate, field)
                            search_conditions.append(column.ilike(search_term))
                    if search_conditions:
                        query = query.filter(or_(*search_conditions))
                
                # Gestione filtri per form (senza JOIN aggiuntivi)
                elif filter_key == 'form_name':
                    query = query.filter(DynamicForm.name.ilike(f'%{filter_value}%'))
                elif filter_key == 'form_category':
                    query = query.filter(DynamicForm.category == filter_value)
                elif filter_key == 'form_subcategory':
                    query = query.filter(DynamicForm.subcategory == filter_value)
                
                # Gestione filtri range età
                elif filter_key == 'age_min':
                    try:
                        min_age = int(filter_value)
                        cutoff_date = date.today().replace(year=date.today().year - min_age)
                        query = query.filter(Candidate.date_of_birth <= cutoff_date)
                    except (ValueError, TypeError):
                        pass
                elif filter_key == 'age_max':
                    try:
                        max_age = int(filter_value)
                        cutoff_date = date.today().replace(year=date.today().year - max_age)
                        query = query.filter(Candidate.date_of_birth >= cutoff_date)
                    except (ValueError, TypeError):
                        pass
                
                # Gestione filtri range altezza
                elif filter_key == 'height_min':
                    try:
                        query = query.filter(Candidate.height_cm >= int(filter_value))
                    except (ValueError, TypeError):
                        pass
                elif filter_key == 'height_max':
                    try:
                        query = query.filter(Candidate.height_cm <= int(filter_value))
                    except (ValueError, TypeError):
                        pass
                
                # Gestione filtri range peso
                elif filter_key == 'weight_min':
                    try:
                        query = query.filter(Candidate.weight_kg >= int(filter_value))
                    except (ValueError, TypeError):
                        pass
                elif filter_key == 'weight_max':
                    try:
                        query = query.filter(Candidate.weight_kg <= int(filter_value))
                    except (ValueError, TypeError):
                        pass
                
                # Gestione filtri per punteggi
                elif filter_key == 'score_ranges' and isinstance(filter_value, list):
                    # Per i filtri di punteggio, dobbiamo filtrare dopo la query
                    # perché il calcolo del punteggio totale è complesso
                    # Salviamo i range per il filtraggio post-query
                    score_ranges_to_filter = filter_value
                
                # Gestione filtri per array (checkbox multipli)
                elif isinstance(filter_value, list) and filter_value:
                    print(f"DEBUG: Processando filtro array {filter_key}: {filter_value}")  # Debug
                    if hasattr(Candidate, filter_key):
                        column = getattr(Candidate, filter_key)
                        # Crea condizioni OR per i valori nell'array
                        conditions = []
                        for value in filter_value:
                            if isinstance(value, str):
                                conditions.append(column.ilike(f'%{value}%'))
                            else:
                                conditions.append(column == value)
                        if conditions:
                            print(f"DEBUG: Applicando {len(conditions)} condizioni per {filter_key}")  # Debug
                            query = query.filter(or_(*conditions))
                    else:
                        print(f"DEBUG: Campo {filter_key} non trovato nel modello Candidate")  # Debug
                
                # Gestione filtri standard per campo esatto
                elif hasattr(Candidate, filter_key):
                    column = getattr(Candidate, filter_key)
                    if isinstance(filter_value, str):
                        # Per i filtri di testo, usa LIKE per matching parziale
                        if filter_key in ['city', 'nationality', 'occupation', 'come_sei_arrivato']:
                            query = query.filter(column.ilike(f'%{filter_value}%'))
                        else:
                            # Per altri campi stringa, match esatto
                            query = query.filter(column == filter_value)
                    else:
                        query = query.filter(column == filter_value)
        
        candidates = query.all()
        
        # Applica filtri post-query per i punteggi se necessario
        if score_ranges_to_filter:
            filtered_candidates = []
            for candidate in candidates:
                total_score = candidate.get_total_score()
                should_include = False
                
                for score_range in score_ranges_to_filter:
                    if score_range == 'no-score':
                        # Candidati senza punteggi
                        if total_score == 0:
                            should_include = True
                            break
                    elif '-' in score_range:
                        try:
                            min_score, max_score = map(float, score_range.split('-'))
                            if min_score <= total_score <= max_score:
                                should_include = True
                                break
                        except (ValueError, TypeError):
                            continue
                
                if should_include:
                    filtered_candidates.append(candidate)
            
            candidates = filtered_candidates
        
        # Filtra solo i campi richiesti
        result = []
        for candidate in candidates:
            candidate_data = {}
            for field in self.fields:
                if field == 'profile_photo':
                    # Gestione speciale per le foto profilo
                    if candidate.photos:
                        # Prendi la prima foto come foto profilo
                        photo = candidate.photos[0]
                        try:
                            secure_url = get_secure_image_url(photo.filename)
                            candidate_data[field] = secure_url
                        except:
                            candidate_data[field] = None
                    else:
                        candidate_data[field] = None
                elif field == 'total_score':
                    # Gestione speciale per il punteggio totale
                    candidate_data[field] = candidate.get_total_score()
                elif field == 'form_name':
                    # Gestione speciale per il nome del form
                    candidate_data[field] = candidate.form.name if candidate.form else None
                elif field == 'form_category':
                    # Gestione speciale per la categoria del form (azienda)
                    candidate_data[field] = candidate.form.category if candidate.form else None
                elif field == 'form_subcategory':
                    # Gestione speciale per la sottocategoria del form (evento)
                    candidate_data[field] = candidate.form.subcategory if candidate.form else None
                elif hasattr(candidate, field):
                    value = getattr(candidate, field)
                    # Converti datetime e date in stringhe
                    if hasattr(value, 'strftime'):
                        candidate_data[field] = value.strftime('%d/%m/%Y')
                    else:
                        candidate_data[field] = value
            result.append(candidate_data)
        
        return result
    
    def __repr__(self):
        return f"<ShareLink {self.token} expires={self.expires_at}>"


class FeatureFlag(db.Model):
    """Modello per gestire le funzionalità attivabili/disattivabili dal developer"""
    id = db.Column(db.Integer, primary_key=True)
    feature_key = db.Column(db.String(64), unique=True, nullable=False)  # chiave unica della funzionalità
    feature_name = db.Column(db.String(128), nullable=False)  # nome leggibile della funzionalità
    description = db.Column(db.Text, nullable=True)  # descrizione dettagliata
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)  # se la funzionalità è attiva
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeatureFlag {self.feature_key}: {'enabled' if self.is_enabled else 'disabled'}>"

    @staticmethod
    def is_feature_enabled(feature_key):
        """Controlla se una funzionalità è abilitata"""
        feature = FeatureFlag.query.filter_by(feature_key=feature_key).first()
        return feature.is_enabled if feature else True  # default enabled se non configurata

    @staticmethod
    def get_all_features():
        """Ottieni tutte le feature flags"""
        return FeatureFlag.query.all()

    @staticmethod
    def create_or_update_feature(feature_key, feature_name, description=None, is_enabled=True):
        """Crea o aggiorna una feature flag"""
        feature = FeatureFlag.query.filter_by(feature_key=feature_key).first()
        if feature:
            feature.feature_name = feature_name
            feature.description = description
            feature.is_enabled = is_enabled
            feature.updated_at = datetime.utcnow()
        else:
            feature = FeatureFlag(
                feature_key=feature_key,
                feature_name=feature_name,
                description=description,
                is_enabled=is_enabled
            )
            db.session.add(feature)
        db.session.commit()
        return feature



