from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from w3form import db
from w3form.models import Candidate, Photo, Curriculum, DynamicForm, Score, User
from w3form.decorators import role_required
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

@api.route('/upload', methods=['POST'])
def upload_candidate_api():
    data = request.form
    files = request.files
    try:
        auto_moto_munito = data.get('auto_moto_munito')
        if auto_moto_munito is not None:
            auto_moto_munito = str(auto_moto_munito).lower() in ['1', 'true', 'on']
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
            country_of_residence=data.get('country_of_residenza'),
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
            auto_moto_munito=auto_moto_munito,
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
            codice_fiscale=data.get('codice_fiscale'),
            permesso_soggiorno=data.get('permesso_soggiorno'),
            come_sei_arrivato=data.get('come_sei_arrivato'),
            form_id=data.get('form_id'),
        )
        db.session.add(c)
        db.session.flush()  # Per ottenere l'id
        # Gestione file immagine profilo
        if 'profile_photo' in files and files['profile_photo'].filename:
            photo_file = files['profile_photo']
            filename = secure_filename(photo_file.filename)
            url = upload_to_azure(photo_file, filename)
            photo = Photo(candidate_id=c.id, filename=url)
            db.session.add(photo)
        # Gestione file curriculum
        if 'curriculum_file' in files and files['curriculum_file'].filename:
            cv_file = files['curriculum_file']
            filename = secure_filename(cv_file.filename)
            url = upload_to_azure(cv_file, filename)
            curriculum = Curriculum(candidate_id=c.id, filename=url)
            db.session.add(curriculum)
        db.session.commit()
        return jsonify({'success': True, 'candidate_id': c.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Ottieni tutti i candidati (con paginazione opzionale)
@api.route('/', methods=['GET'])
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
