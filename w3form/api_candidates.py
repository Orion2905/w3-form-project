from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from w3form import db
from w3form.models import Candidate, Photo, Curriculum, DynamicForm, Score, User, FormFieldConfiguration
from w3form.decorators import role_required, view_only_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from w3form.azure_utils import upload_to_azure
from sqlalchemy import func, text
import sqlalchemy

api = Blueprint('api', __name__, url_prefix='/api/candidates')
api_stats = Blueprint('api_stats', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility per serializzare un candidato

def candidate_to_dict(c):
    return {
        'id': c.id,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'gender': c.gender,
        'date_of_birth': c.date_of_birth.isoformat() if c.date_of_birth else None,
        'place_of_birth': c.place_of_birth,
        'nationality': c.nationality,
        'marital_status': c.marital_status,
        'height_cm': c.height_cm,
        'weight_kg': c.weight_kg,
        'tshirt_size': c.tshirt_size,
        'shoe_size_eu': c.shoe_size_eu,
        'phone_number': c.phone_number,
        'email': c.email,
        'address': c.address,
        'city': c.city,
        'postal_code': c.postal_code,
        'country_of_residence': c.country_of_residence,
        'id_document': c.id_document,
        'id_number': c.id_number,
        'id_expiry_date': c.id_expiry_date.isoformat() if c.id_expiry_date else None,
        'id_country': c.id_country,
        'license_country': c.license_country,
        'license_number': c.license_number,
        'license_category': c.license_category,
        'license_issue_date': c.license_issue_date.isoformat() if c.license_issue_date else None,
        'license_expiry_date': c.license_expiry_date.isoformat() if c.license_expiry_date else None,
        'years_driving_experience': c.years_driving_experience,
        'auto_moto_munito': c.auto_moto_munito,
        'occupation': c.occupation,
        'other_experience': c.other_experience,
        'availability_from': c.availability_from.isoformat() if c.availability_from else None,
        'availability_till': c.availability_till.isoformat() if c.availability_till else None,
        'city_availability': c.city_availability,
        'additional_document': c.additional_document,
        'codice_fiscale': c.codice_fiscale,
        'permesso_soggiorno': c.permesso_soggiorno,
        'language_1': c.language_1,
        'proficiency_1': c.proficiency_1,
        'language_2': c.language_2,
        'proficiency_2': c.proficiency_2,
        'language_3': c.language_3,
        'proficiency_3': c.proficiency_3,
        'archived': c.archived,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'form_name': c.form.name if c.form else None,
        'form_category': c.form.category if c.form else None,
        'form_subcategory': c.form.subcategory if c.form else None,
        'scores': {
            'total_score': c.get_total_score(),
            'average_score': c.get_average_score(),
            'count': len(c.scores),
            'summary': c.get_score_summary()
        } if hasattr(c, 'scores') else {'total_score': 0, 'average_score': 0, 'count': 0, 'summary': {}},
    }

# Aggiungi candidato
@api.route('/', methods=['POST'])
@login_required
@role_required('intervistatore')
def add_candidate_api():
    data = request.json
    try:
        c = Candidate(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            gender=data.get('gender'),
            date_of_birth=datetime.fromisoformat(data.get('date_of_birth')) if data.get('date_of_birth') else None,
            place_of_birth=data.get('place_of_birth'),
            nationality=data.get('nationality'),
            marital_status=data.get('marital_status'),
            height_cm=data.get('height_cm'),
            weight_kg=data.get('weight_kg'),
            tshirt_size=data.get('tshirt_size'),
            shoe_size_eu=data.get('shoe_size_eu'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            address=data.get('address'),
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            country_of_residence=data.get('country_of_residence'),
            id_document=data.get('id_document'),
            id_number=data.get('id_number'),
            id_expiry_date=datetime.fromisoformat(data.get('id_expiry_date')) if data.get('id_expiry_date') else None,
            id_country=data.get('id_country'),
            additional_document=data.get('additional_document'),
            license_country=data.get('license_country'),
            license_number=data.get('license_number'),
            license_category=data.get('license_category'),
            license_issue_date=datetime.fromisoformat(data.get('license_issue_date')) if data.get('license_issue_date') else None,
            license_expiry_date=datetime.fromisoformat(data.get('license_expiry_date')) if data.get('license_expiry_date') else None,
            years_driving_experience=data.get('years_driving_experience'),
            auto_moto_munito=data.get('auto_moto_munito'),
            occupation=data.get('occupation'),
            other_experience=data.get('other_experience'),
            availability_from=datetime.fromisoformat(data.get('availability_from')) if data.get('availability_from') else None,
            availability_till=datetime.fromisoformat(data.get('availability_till')) if data.get('availability_till') else None,
            city_availability=data.get('other_location'),
            language_1=data.get('language_1'),
            proficiency_1=data.get('proficiency_1'),
            language_2=data.get('language_2'),
            proficiency_2=data.get('proficiency_2'),
            language_3=data.get('language_3'),
            proficiency_3=data.get('proficiency_3'),
        )
        db.session.add(c)
        db.session.commit()
        return jsonify({'success': True, 'candidate': candidate_to_dict(c)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Modifica candidato
@api.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('intervistatore')
def update_candidate_api(id):
    c = Candidate.query.get_or_404(id)
    
    # Gestisce sia JSON che FormData
    if request.content_type and 'application/json' in request.content_type:
        data = request.json
        print(f"DEBUG: Dati JSON ricevuti: {data}")
    else:
        data = request.form.to_dict()
        print(f"DEBUG: Dati FormData ricevuti: {data}")
        
        # Gestione upload foto se presente
        if 'profile_photo' in request.files:
            photo_file = request.files['profile_photo']
            if photo_file.filename:
                try:
                    filename = secure_filename(photo_file.filename)
                    url = upload_to_azure(photo_file, filename)
                    
                    # Rimuovi foto esistente se presente
                    existing_photo = Photo.query.filter_by(candidate_id=id).first()
                    if existing_photo:
                        db.session.delete(existing_photo)
                    
                    # Aggiungi nuova foto
                    photo = Photo(candidate_id=id, filename=url)
                    db.session.add(photo)
                    print(f"DEBUG: Foto caricata: {url}")
                except Exception as e:
                    print(f"DEBUG: Errore caricamento foto: {e}")
    
    try:
        print(f"DEBUG: Aggiornamento candidato {id}")
        
        # Lista dei campi con le loro conversioni di tipo
        field_conversions = {
            'height_cm': lambda x: int(x) if x and x.strip() else None,
            'weight_kg': lambda x: int(x) if x and x.strip() else None,
            'shoe_size_eu': lambda x: int(x) if x and x.strip() else None,
            'years_driving_experience': lambda x: int(x) if x and x.strip() else None,
        }
        
        # Aggiorna i campi
        for field in candidate_to_dict(c).keys():
            if field in data and field != 'id':  # Non aggiornare l'ID
                value = data[field]
                
                # Gestione valori vuoti
                if value == '' or value is None:
                    setattr(c, field, None)
                    continue
                
                # Conversioni specifiche per tipo
                if field in field_conversions:
                    try:
                        value = field_conversions[field](value)
                    except (ValueError, TypeError):
                        value = None
                elif 'date' in field and value:
                    try:
                        if isinstance(value, str):
                            # Gestisce formato YYYY-MM-DD
                            setattr(c, field, datetime.strptime(value, '%Y-%m-%d').date())
                            continue
                    except ValueError:
                        print(f"DEBUG: Errore conversione data per {field}: {value}")
                        continue
                
                setattr(c, field, value)
                print(f"DEBUG: Aggiornato {field} = {value}")
        
        db.session.commit()
        print(f"DEBUG: Candidato {id} aggiornato con successo")
        return jsonify({'success': True, 'candidate': candidate_to_dict(c)})
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Errore aggiornamento candidato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

# Elimina candidato
@api.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('intervistatore')
def delete_candidate_api(id):
    c = Candidate.query.get_or_404(id)
    try:
        db.session.delete(c)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Aggiungi candidato con upload file
@api.route('/uploadfile', methods=['POST'])
@login_required
@role_required('intervistatore')
def upload_file_api():
    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'error': 'Nessun file inviato'}), 400
    filename = secure_filename(file.filename)
    try:
        url = upload_to_azure(file, filename)
        return jsonify({'success': True, 'url': url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def filter_visible_fields(form_data, form_id):
    """
    Filtra i dati del form mantenendo solo i campi visibili secondo la configurazione.
    
    Args:
        form_data: Dati dal form (request.form)
        form_id: ID del form dinamico
        
    Returns:
        dict: Dati filtrati con solo i campi visibili
    """
    try:
        # Recupera la configurazione dei campi per questo form
        field_config = FormFieldConfiguration.get_form_configuration(form_id)
        
        # Se non c'è configurazione, restituisci tutti i dati (fallback)
        if not field_config:
            print(f"⚠️ Nessuna configurazione trovata per form {form_id}, usando tutti i campi")
            return dict(form_data)
        
        # Campi che devono sempre essere inclusi indipendentemente dalla configurazione
        essential_fields = [
            'form_id', 'gdpr_consent', 'first_name', 'last_name', 'email'
        ]
        
        # Filtra solo i campi visibili
        filtered_data = {}
        visible_fields = []
        
        # Prima aggiungi i campi essenziali se presenti
        for field in essential_fields:
            if field in form_data:
                filtered_data[field] = form_data.get(field)
                if field not in visible_fields:
                    visible_fields.append(field)
                print(f"✅ Campo essenziale incluso: {field}")
        
        # Poi aggiungi i campi configurati come visibili
        for field_name, config in field_config.items():
            if config.is_visible:  # Accesso diretto alla proprietà dell'oggetto
                if field_name in form_data and field_name not in filtered_data:
                    filtered_data[field_name] = form_data.get(field_name)
                    visible_fields.append(field_name)
        
        print(f"✅ Campi visibili filtrati ({len(visible_fields)}): {visible_fields}")
        print(f"📊 Campi totali ricevuti: {len(form_data)}, Campi filtrati: {len(filtered_data)}")
        
        return filtered_data
        
    except Exception as e:
        print(f"❌ Errore nel filtraggio campi: {e}")
        # In caso di errore, restituisci tutti i dati per sicurezza
        return dict(form_data)

@api.route('/upload', methods=['POST'])
@login_required
@role_required('intervistatore')
def upload_candidate_api():
    original_data = request.form
    files = request.files
    
    try:
        # Ottieni il form_id per determinare quali campi filtrare
        form_id = original_data.get('form_id')
        if not form_id:
            return jsonify({'success': False, 'error': 'form_id mancante'}), 400
        
        # Filtra i dati mantenendo solo i campi visibili
        data = filter_visible_fields(original_data, form_id)
        
        auto_moto_munito = data.get('auto_moto_munito')
        if auto_moto_munito is not None:
            auto_moto_munito = str(auto_moto_munito).lower() in ['1', 'true', 'on']
        
        # Crea il candidato solo con i campi visibili e non vuoti
        candidate_data = {}
        
        # Campi di testo semplici
        text_fields = [
            'first_name', 'last_name', 'gender', 'place_of_birth', 'nationality', 'marital_status',
            'height_cm', 'weight_kg', 'tshirt_size', 'shoe_size_eu', 'phone_number', 'email',
            'address', 'city', 'postal_code', 'country_of_residence', 'id_document', 'id_number',
            'id_country', 'additional_document', 'license_country', 'license_number', 
            'license_category', 'years_driving_experience', 'occupation', 'other_experience',
            'city_availability', 'language_1', 'proficiency_1', 'language_2', 'proficiency_2',
            'language_3', 'proficiency_3', 'codice_fiscale', 'permesso_soggiorno', 
            'come_sei_arrivato', 'form_id'
        ]
        
        # Recupera la configurazione per determinare la visibilità
        field_config = FormFieldConfiguration.get_form_configuration(form_id)
        
        for field in text_fields:
            if field in data and data.get(field):
                # Il campo è presente e ha un valore
                candidate_data[field] = data.get(field)
            elif field_config and field in field_config and not field_config[field].is_visible:
                # Il campo è nascosto nella configurazione, passa stringa vuota invece di NULL
                if field in ['first_name', 'last_name', 'email']:
                    # Per campi essenziali, usa un valore di default significativo
                    if field == 'first_name':
                        candidate_data[field] = '[Nome nascosto]'
                    elif field == 'last_name':
                        candidate_data[field] = '[Cognome nascosto]'
                    elif field == 'email':
                        candidate_data[field] = 'hidden@example.com'
                else:
                    # Per altri campi, usa stringa vuota
                    candidate_data[field] = ''
                print(f"🚫 Campo nascosto {field}, usando valore di default")
            elif field in ['first_name', 'last_name', 'email']:
                # Campi essenziali devono sempre avere un valore, anche se vuoto nel form
                candidate_data[field] = data.get(field, '')
        
        # Campi data con conversione
        date_fields = {
            'date_of_birth': 'date_of_birth',
            'id_expiry_date': 'id_expiry_date', 
            'license_issue_date': 'license_issue_date',
            'license_expiry_date': 'license_expiry_date',
            'availability_from': 'availability_from',
            'availability_till': 'availability_till'
        }
        
        for field_name, attr_name in date_fields.items():
            if field_name in data and data.get(field_name):
                try:
                    candidate_data[attr_name] = datetime.fromisoformat(data.get(field_name))
                except (ValueError, TypeError):
                    print(f"⚠️ Errore conversione data per campo {field_name}: {data.get(field_name)}")
            elif field_config and field_name in field_config and not field_config[field_name].is_visible:
                # Campo data nascosto - non aggiungere nulla (rimane NULL che è permesso per le date)
                print(f"🚫 Campo data nascosto {field_name}, omesso dal salvataggio")
        
        # Campo booleano speciale
        if 'auto_moto_munito' in data:
            candidate_data['auto_moto_munito'] = auto_moto_munito
        elif field_config and 'auto_moto_munito' in field_config and not field_config['auto_moto_munito'].is_visible:
            # Campo nascosto - usa False come default per booleani
            candidate_data['auto_moto_munito'] = False
            print(f"🚫 Campo booleano nascosto auto_moto_munito, usando False")
            
        # Gestione del campo country_of_residence (può avere nomi diversi)
        if 'country_of_residenza' in data and data.get('country_of_residenza'):
            candidate_data['country_of_residence'] = data.get('country_of_residenza')
        
        print(f"📝 Creazione candidato con {len(candidate_data)} campi: {list(candidate_data.keys())}")
        
        c = Candidate(**candidate_data)
        db.session.add(c)
        db.session.flush()  # Per ottenere l'id
        
        # Recupera la configurazione per verificare la visibilità dei campi file
        field_config = FormFieldConfiguration.get_form_configuration(form_id)
        
        # Gestione file immagine profilo (solo se il campo è visibile)
        if 'profile_photo' in files and files['profile_photo'].filename:
            # Controlla se il campo profile_photo è visibile nella configurazione
            if not field_config or 'profile_photo' not in field_config or field_config['profile_photo'].is_visible:
                photo_file = files['profile_photo']
                filename = secure_filename(photo_file.filename)
                url = upload_to_azure(photo_file, filename)
                photo = Photo(candidate_id=c.id, filename=url)
                db.session.add(photo)
                print("📷 File foto profilo salvato (campo visibile)")
            else:
                print("🚫 File foto profilo ignorato (campo nascosto)")
                
        # Gestione file curriculum (solo se il campo è visibile)
        if 'curriculum_file' in files and files['curriculum_file'].filename:
            # Controlla se il campo curriculum_file è visibile nella configurazione
            if not field_config or 'curriculum_file' not in field_config or field_config['curriculum_file'].is_visible:
                cv_file = files['curriculum_file']
                filename = secure_filename(cv_file.filename)
                url = upload_to_azure(cv_file, filename)
                curriculum = Curriculum(candidate_id=c.id, filename=url)
                db.session.add(curriculum)
                print("📄 File curriculum salvato (campo visibile)")
            else:
                print("🚫 File curriculum ignorato (campo nascosto)")
        db.session.commit()
        return jsonify({'success': True, 'candidate_id': c.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Ottieni tutti i candidati (con paginazione opzionale)
@api.route('/', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def get_candidates_api():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    query = Candidate.query.order_by(Candidate.id.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    candidates = [candidate_to_dict(c) for c in pagination.items]
    return jsonify({
        'success': True,
        'candidates': candidates,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    })

# Ottieni un singolo candidato per id
@api.route('/<int:id>', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def get_candidate_api(id):
    c = Candidate.query.get_or_404(id)
    return jsonify({'success': True, 'candidate': candidate_to_dict(c)})

api_stats = Blueprint('api_stats', __name__)

@api_stats.route('/api/stats/summary')
def stats_summary():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    base_query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        base_query = base_query.join(DynamicForm)
        if evento:
            base_query = base_query.filter(DynamicForm.category == evento)
        if azienda:
            base_query = base_query.filter(DynamicForm.subcategory == azienda)
    
    total = base_query.count()
    
    # Per CV e Photo, riapplico i filtri 
    cv_query = base_query.join(Curriculum)
    with_cv = cv_query.count()
    
    photo_query = base_query.join(Photo)
    with_photo = photo_query.count()
    
    return jsonify({
        'total': total,
        'with_cv': with_cv,
        'with_photo': with_photo
    })

@api_stats.route('/api/stats/roles')
def stats_roles():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        query = query.join(DynamicForm)
        if evento:
            query = query.filter(DynamicForm.category == evento)
        if azienda:
            query = query.filter(DynamicForm.subcategory == azienda)
    
    # Distribuzione per occupation (professione)
    data = query.with_entities(Candidate.occupation, func.count()).group_by(Candidate.occupation).all()
    return jsonify({r or 'Non specificato': c for r, c in data})

@api_stats.route('/api/stats/monthly')
def stats_monthly():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Compatibilità SQL Server/SQLite: format per SQL Server, strftime per SQLite
    if db.engine.url.get_backend_name() == 'mssql':
        month_sql = "format(created_at, 'yyyy-MM')"
        query = db.session.query(
            text(f"{month_sql} as month"),
            func.count()
        ).select_from(Candidate)
        
        # Applica filtri se specificati
        if evento or azienda:
            query = query.join(DynamicForm)
            if evento:
                query = query.filter(DynamicForm.category == evento)
            if azienda:
                query = query.filter(DynamicForm.subcategory == azienda)
        
        data = query.group_by(text(month_sql)).all()
    else:
        month_expr = func.strftime('%Y-%m', Candidate.created_at)
        query = db.session.query(
            month_expr.label('month'),
            func.count()
        )
        
        # Applica filtri se specificati
        if evento or azienda:
            query = query.join(DynamicForm)
            if evento:
                query = query.filter(DynamicForm.category == evento)
            if azienda:
                query = query.filter(DynamicForm.subcategory == azienda)
        
        data = query.group_by(month_expr).all()
    return jsonify({m: c for m, c in data if m})

@api_stats.route('/api/stats/latest')
def stats_latest():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        query = query.join(DynamicForm)
        if evento:
            query = query.filter(DynamicForm.category == evento)
        if azienda:
            query = query.filter(DynamicForm.subcategory == azienda)
    
    latest = query.order_by(Candidate.created_at.desc()).limit(50).all()
    return jsonify([
        {
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email,
            'city': c.city,
            'gender': c.gender,
            'created_at': c.created_at.strftime('%Y-%m-%d'),
            'role': getattr(c, 'occupation', None) or getattr(c, 'role', None)
        } for c in latest
    ])

@api_stats.route('/api/stats/gender')
def stats_gender():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        query = query.join(DynamicForm)
        if evento:
            query = query.filter(DynamicForm.category == evento)
        if azienda:
            query = query.filter(DynamicForm.subcategory == azienda)
    
    data = query.with_entities(Candidate.gender, func.count()).group_by(Candidate.gender).all()
    return jsonify({g or 'Non specificato': c for g, c in data})

@api_stats.route('/api/stats/marital_status')
def stats_marital_status():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        query = query.join(DynamicForm)
        if evento:
            query = query.filter(DynamicForm.category == evento)
        if azienda:
            query = query.filter(DynamicForm.subcategory == azienda)
    
    data = query.with_entities(Candidate.marital_status, func.count()).group_by(Candidate.marital_status).all()
    return jsonify({s or 'Non specificato': c for s, c in data})

@api_stats.route('/api/stats/tshirt_size')
def stats_tshirt_size():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        query = query.join(DynamicForm)
        if evento:
            query = query.filter(DynamicForm.category == evento)
        if azienda:
            query = query.filter(DynamicForm.subcategory == azienda)
    
    data = query.with_entities(Candidate.tshirt_size, func.count()).group_by(Candidate.tshirt_size).all()
    return jsonify({t or 'Non specificata': c for t, c in data})

@api_stats.route('/api/stats/auto_moto_munito')
def stats_auto_moto_munito():
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        query = query.join(DynamicForm)
        if evento:
            query = query.filter(DynamicForm.category == evento)
        if azienda:
            query = query.filter(DynamicForm.subcategory == azienda)
    
    data = query.with_entities(Candidate.auto_moto_munito, func.count()).group_by(Candidate.auto_moto_munito).all()
    return jsonify({('Sì' if b else 'No') if b is not None else 'Non specificato': c for b, c in data})

@api_stats.route('/api/stats/eventi')
def stats_eventi():
    """Ottiene la lista di tutti gli eventi (categorie dei form) disponibili"""
    data = DynamicForm.query.with_entities(DynamicForm.category).filter(DynamicForm.category.isnot(None)).distinct().all()
    eventi = [item[0] for item in data if item[0]]
    return jsonify(eventi)

@api_stats.route('/api/stats/aziende')
def stats_aziende():
    """Ottiene la lista di tutte le aziende (sottocategorie dei form) disponibili"""
    data = DynamicForm.query.with_entities(DynamicForm.subcategory).filter(DynamicForm.subcategory.isnot(None)).distinct().all()
    aziende = [item[0] for item in data if item[0]]
    return jsonify(aziende)

@api_stats.route('/api/stats/cities')
def stats_cities():
    """Ottiene la distribuzione dei candidati per città (top 10)"""
    # Ottieni i filtri dalla query string
    evento = request.args.get('evento', '')
    azienda = request.args.get('azienda', '')
    
    # Base query
    query = Candidate.query
    
    # Applica filtri se specificati
    if evento or azienda:
        query = query.join(DynamicForm)
        if evento:
            query = query.filter(DynamicForm.category == evento)
        if azienda:
            query = query.filter(DynamicForm.subcategory == azienda)
    
    # Raggruppa per città e conta, prendi solo le top 10
    data = query.with_entities(Candidate.city, func.count())\
                .filter(Candidate.city.isnot(None))\
                .group_by(Candidate.city)\
                .order_by(func.count().desc())\
                .limit(10).all()
    
    return jsonify({c or 'Non specificata': count for c, count in data})


# ===== ROUTE PER LA CONDIVISIONE =====

@api.route('/share', methods=['POST'])
@login_required
def create_share_link():
    """
    Crea un nuovo link di condivisione per la lista candidati
    """
    import secrets
    from w3form.models import ShareLink
    from datetime import timedelta
    
    try:
        data = request.get_json()
        
        # Validazione input
        if not data.get('fields'):
            return jsonify({'success': False, 'error': 'Nessun campo selezionato'}), 400
        
        # Genera token univoco
        token = secrets.token_urlsafe(32)
        while ShareLink.query.filter_by(token=token).first():
            token = secrets.token_urlsafe(32)
        
        # Crea il link condiviso
        share_link = ShareLink(
            token=token,
            fields=data.get('fields', []),
            filters=data.get('filters', {}),
            scope=data.get('scope', 'all'),
            archived=data.get('archived', False),
            created_by=current_user.email if hasattr(current_user, 'email') else 'user'
        )
        
        # Imposta password se fornita
        if data.get('password'):
            share_link.set_password(data.get('password'))
        
        # Imposta scadenza se fornita
        if data.get('expiry_days'):
            days = int(data.get('expiry_days'))
            share_link.expires_at = datetime.utcnow() + timedelta(days=days)
        
        db.session.add(share_link)
        db.session.commit()
        
        # Costruisci URL completo
        share_url = request.url_root.rstrip('/') + f'/shared/{token}'
        
        return jsonify({
            'success': True,
            'share_url': share_url,
            'token': token,
            'expires_at': share_link.expires_at.isoformat() if share_link.expires_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/shares/cleanup', methods=['POST'])
@login_required
def cleanup_expired_shares():
    """
    Elimina tutti i link condivisi scaduti dell'utente
    """
    from w3form.models import ShareLink
    
    try:
        user_email = current_user.email if hasattr(current_user, 'email') else 'user'
        
        # Trova tutti i link scaduti dell'utente
        expired_links = ShareLink.query.filter_by(created_by=user_email)\
                                      .filter(ShareLink.expires_at < datetime.utcnow())\
                                      .all()
        
        count = len(expired_links)
        
        # Elimina i link scaduti
        for link in expired_links:
            db.session.delete(link)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'deleted_count': count,
            'message': f'Eliminati {count} link scaduti'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/shares/<int:share_id>/extend', methods=['POST'])
@login_required
def extend_share_expiry(share_id):
    """
    Estende la scadenza di un link condiviso
    """
    from w3form.models import ShareLink
    from datetime import timedelta
    
    try:
        data = request.get_json()
        days = int(data.get('days', 7))
        
        share_link = ShareLink.query.get_or_404(share_id)
        
        # Controlla che l'utente sia il proprietario
        user_email = current_user.email if hasattr(current_user, 'email') else 'user'
        if share_link.created_by != user_email:
            return jsonify({'success': False, 'error': 'Non autorizzato'}), 403
        
        # Estende la scadenza
        share_link.expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_expiry': share_link.expires_at.isoformat(),
            'message': f'Scadenza estesa di {days} giorni'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
