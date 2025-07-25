from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
    session,
    send_file,
    Response,
    make_response
)
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import joinedload
from w3form import db
from w3form.models import (
    User, Candidate, DynamicForm, Score, ScoreCategory, SystemSettings, FormFieldConfiguration
)
from w3form.decorators import role_required, developer_required, view_only_required
from w3form.azure_utils import get_secure_image_url, get_secure_document_url
import requests, time
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import json
import csv
from datetime import datetime, date
from flask import abort
from io import BytesIO, StringIO
from azure.storage.blob import BlobServiceClient



main = Blueprint("main", __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Credenziali non valide', 'danger')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/')
@login_required
def dashboard():
    candidates = Candidate.query.all()
    breadcrumbs = [
        {'name': 'Dashboard', 'url': None}
    ]
    return render_template('dashboard.html', candidates=candidates, sidebar=True, breadcrumbs=breadcrumbs)

@main.route('/candidato/aggiungi', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def add_candidate():
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': url_for('main.candidates_list')},
        {'name': 'Aggiungi Candidato', 'url': None}
    ]
    # TODO: implementare form e logica inserimento
    return render_template('candidate_form.html', breadcrumbs=breadcrumbs)

@main.route('/candidati')
@login_required
@view_only_required('intervistatore')
def candidates_list():
    candidates = Candidate.query.all()
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': None}
    ]
    return render_template('candidates_list.html', candidates=candidates, breadcrumbs=breadcrumbs)

@main.route('/candidati/archiviati')
@login_required
@role_required('intervistatore')
def archived_candidates_list():
    """Vista per candidati archiviati"""
    candidates = Candidate.query.filter_by(archived=True).all()
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': url_for('main.candidates_list')},
        {'name': 'Candidati Archiviati', 'url': None}
    ]
    return render_template('candidates_list.html', candidates=candidates, archived=True, breadcrumbs=breadcrumbs)

@main.route('/candidati/modifica/<int:candidate_id>', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def edit_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    if request.method == 'POST':
        print(f"DEBUG: POST request ricevuto per candidato {candidate_id}")
        print(f"DEBUG: Form data keys: {list(request.form.keys())}")
        print(f"DEBUG: first_name from form: '{request.form.get('first_name')}'")
        
        # Campi obbligatori
        candidate.first_name = request.form.get('first_name', '').strip()
        candidate.last_name = request.form.get('last_name', '').strip()
        candidate.email = request.form.get('email', '').strip()
        
        # Campi anagrafica
        candidate.gender = request.form.get('gender') or None
        candidate.phone_number = request.form.get('phone_number') or None
        candidate.place_of_birth = request.form.get('place_of_birth') or None
        candidate.nationality = request.form.get('nationality') or None
        candidate.marital_status = request.form.get('marital_status') or None
        candidate.come_sei_arrivato = request.form.get('come_sei_arrivato') or None
        candidate.height_cm = int(request.form.get('height_cm')) if request.form.get('height_cm') else None
        candidate.weight_kg = int(request.form.get('weight_kg')) if request.form.get('weight_kg') else None
        candidate.tshirt_size = request.form.get('tshirt_size') or None
        candidate.shoe_size_eu = int(request.form.get('shoe_size_eu')) if request.form.get('shoe_size_eu') else None
        
        # Date
        if request.form.get('date_of_birth'):
            candidate.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        else:
            candidate.date_of_birth = None
            
        # Contatti
        candidate.address = request.form.get('address') or None
        candidate.city = request.form.get('city') or None
        candidate.postal_code = request.form.get('postal_code') or None
        candidate.country_of_residence = request.form.get('country_of_residence') or None
        
        # Documenti
        candidate.id_document = request.form.get('id_document') or None
        candidate.id_number = request.form.get('id_number') or None
        candidate.id_country = request.form.get('id_country') or None
        candidate.codice_fiscale = request.form.get('codice_fiscale') or None
        candidate.permesso_soggiorno = request.form.get('permesso_soggiorno') or None
        candidate.additional_document = request.form.get('additional_document') or None
        
        if request.form.get('id_expiry_date'):
            candidate.id_expiry_date = datetime.strptime(request.form.get('id_expiry_date'), '%Y-%m-%d').date()
        else:
            candidate.id_expiry_date = None
            
        # Patente
        candidate.license_country = request.form.get('license_country') or None
        candidate.license_number = request.form.get('license_number') or None
        candidate.license_category = request.form.get('license_category') or None
        candidate.years_driving_experience = int(request.form.get('years_driving_experience')) if request.form.get('years_driving_experience') else None
        candidate.auto_moto_munito = request.form.get('auto_moto_munito') == 'True' if request.form.get('auto_moto_munito') else None
        
        if request.form.get('license_issue_date'):
            candidate.license_issue_date = datetime.strptime(request.form.get('license_issue_date'), '%Y-%m-%d').date()
        else:
            candidate.license_issue_date = None
            
        if request.form.get('license_expiry_date'):
            candidate.license_expiry_date = datetime.strptime(request.form.get('license_expiry_date'), '%Y-%m-%d').date()
        else:
            candidate.license_expiry_date = None
            
        # Lingue
        candidate.language_1 = request.form.get('language_1') or None
        candidate.proficiency_1 = request.form.get('proficiency_1') or None
        candidate.language_2 = request.form.get('language_2') or None
        candidate.proficiency_2 = request.form.get('proficiency_2') or None
        candidate.language_3 = request.form.get('language_3') or None
        candidate.proficiency_3 = request.form.get('proficiency_3') or None
        
        # Lavoro
        candidate.occupation = request.form.get('occupation') or None
        candidate.city_availability = request.form.get('city_availability') or None
        candidate.other_experience = request.form.get('other_experience') or None
        
        if request.form.get('availability_from'):
            candidate.availability_from = datetime.strptime(request.form.get('availability_from'), '%Y-%m-%d').date()
        else:
            candidate.availability_from = None
            
        if request.form.get('availability_till'):
            candidate.availability_till = datetime.strptime(request.form.get('availability_till'), '%Y-%m-%d').date()
        else:
            candidate.availability_till = None
        
        try:
            db.session.commit()
            flash('Candidato aggiornato con successo!', 'success')
            return redirect(url_for('main.candidate_profile', candidate_id=candidate.id))
        except Exception as e:
            db.session.rollback()
            flash('Errore durante l\'aggiornamento del candidato.', 'error')
            return redirect(url_for('main.candidate_profile', candidate_id=candidate.id))
            
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': url_for('main.candidates_list')},
        {'name': f'{candidate.first_name} {candidate.last_name}', 'url': url_for('main.candidate_profile', candidate_id=candidate.id)},
        {'name': 'Modifica', 'url': None}
    ]
    
    return render_template('edit_candidate.html', candidate=candidate, breadcrumbs=breadcrumbs)

@main.route('/esporta/pdf')
@login_required
@view_only_required('intervistatore')
def export_pdf():
    # TODO: implementare esportazione PDF
    return 'Funzione esportazione PDF in sviluppo'

@main.route('/esporta/excel')
@login_required
@view_only_required('intervistatore')
def export_excel():
    # TODO: implementare esportazione Excel
    return 'Funzione esportazione Excel in sviluppo'

@main.route('/forms/crea', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def create_dynamic_form():
    dropdown_fields = [
        'gender', 'marital_status', 'tshirt_size', 'id_document', 'license_category',
        'auto_moto_munito', 'proficiency_1', 'proficiency_2', 'proficiency_3', 'come_sei_arrivato'
    ]
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        description = request.form.get('description')
        category = request.form.get('category')  # Nuovo campo categoria
        subcategory = request.form.get('subcategory')  # Nuovo campo sottocategoria
        is_active = bool(request.form.get('is_active'))
        active_from = request.form.get('active_from')
        active_until = request.form.get('active_until')
        dropdown_options = {}
        for field in dropdown_fields:
            key = f'opt_{field}'
            val = request.form.get(key, '').strip()
            if val:
                dropdown_options[field] = [v.strip() for v in val.splitlines() if v.strip()]
        
        # Gestione Privacy Policy
        privacy_policy_enabled = bool(request.form.get('privacy_policy_enabled'))
        privacy_policy_url = request.form.get('privacy_policy_url', '').strip() or None
        privacy_policy_text = request.form.get('privacy_policy_text', '').strip() or "Leggi l'informativa completa sulla privacy"
        privacy_policy_new_tab = bool(request.form.get('privacy_policy_new_tab'))
        
        form = DynamicForm(
            name=name,
            slug=slug,
            description=description,
            category=category,
            subcategory=subcategory,
            dropdown_options=dropdown_options,
            is_active=is_active,
            active_from=datetime.strptime(active_from, '%Y-%m-%dT%H:%M') if active_from else None,
            active_until=datetime.strptime(active_until, '%Y-%m-%dT%H:%M') if active_until else None,
            privacy_policy_enabled=privacy_policy_enabled,
            privacy_policy_url=privacy_policy_url,
            privacy_policy_text=privacy_policy_text,
            privacy_policy_new_tab=privacy_policy_new_tab
        )
        db.session.add(form)
        db.session.commit()
        flash('Form creato! Link: ' + url_for('main.public_dynamic_form', slug=slug, _external=True), 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('dynamic_form_create.html', dropdown_fields=dropdown_fields)

@main.route('/forms')
def list_dynamic_forms():
    forms = DynamicForm.query.all()
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Gestione Form', 'url': None}
    ]
    return render_template('dynamic_form_list.html', forms=forms, breadcrumbs=breadcrumbs)

@main.route('/form/<slug>', methods=['GET'])
def public_dynamic_form(slug):
    form = DynamicForm.query.filter_by(slug=slug).first_or_404()
    now = datetime.utcnow()
    if not form.is_active or (form.active_from and now < form.active_from) or (form.active_until and now > form.active_until):
        return render_template('404.html'), 404
    dropdown_options = form.dropdown_options or {}
    
    # Ottieni la modalità test globale
    test_mode = form.is_test_mode_active()
    
    # Ottieni la configurazione dei campi per questo form
    fields_config = FormFieldConfiguration.get_form_configuration(form.id)
    
    return render_template('dynamic_form_public.html', 
                         form=form, 
                         dropdown_options=dropdown_options,
                         test_mode=test_mode,
                         fields_config=fields_config)


@main.route('/api/form/<slug>/field-visibility', methods=['GET'])
def get_form_field_visibility(slug):
    """API pubblica per ottenere la configurazione di visibilità dei campi di un form"""
    try:
        form = DynamicForm.query.filter_by(slug=slug).first_or_404()
        
        # Ottieni la configurazione dei campi
        fields_config = FormFieldConfiguration.get_form_configuration(form.id)
        default_fields = FormFieldConfiguration.get_default_fields()
        
        # Crea la risposta con visibilità e obbligatorietà
        field_visibility = {}
        for field_name in default_fields.keys():
            config = fields_config.get(field_name)
            field_visibility[field_name] = {
                'is_visible': config.is_visible if config else True,
                'is_required': config.is_required if config else True
            }
        
        return jsonify({
            'success': True,
            'form_slug': slug,
            'field_visibility': field_visibility
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Errore nel caricamento configurazione: {str(e)}'
        }), 500

@main.route('/forms/modifica/<int:form_id>', methods=['GET', 'POST'])
def edit_dynamic_form(form_id):
    form = DynamicForm.query.get_or_404(form_id)
    dropdown_fields = [
        'gender', 'marital_status', 'tshirt_size', 'id_document', 'license_category',
        'auto_moto_munito', 'proficiency_1', 'proficiency_2', 'proficiency_3', 'come_sei_arrivato'
    ]
    if request.method == 'POST':
        form.name = request.form.get('name')
        form.slug = request.form.get('slug')
        form.description = request.form.get('description')
        form.category = request.form.get('category')  # Nuovo campo categoria
        form.subcategory = request.form.get('subcategory')  # Nuovo campo sottocategoria
        form.is_active = bool(request.form.get('is_active'))
        active_from = request.form.get('active_from')
        active_until = request.form.get('active_until')
        form.active_from = datetime.strptime(active_from, '%Y-%m-%dT%H:%M') if active_from else None
        form.active_until = datetime.strptime(active_until, '%Y-%m-%dT%H:%M') if active_until else None
        dropdown_options = {}
        for field in dropdown_fields:
            key = f'opt_{field}'
            val = request.form.get(key, '').strip()
            if val:
                dropdown_options[field] = [v.strip() for v in val.splitlines() if v.strip()]
        form.dropdown_options = dropdown_options
        
        # Gestione Privacy Policy
        form.privacy_policy_enabled = bool(request.form.get('privacy_policy_enabled'))
        form.privacy_policy_url = request.form.get('privacy_policy_url', '').strip() or None
        form.privacy_policy_text = request.form.get('privacy_policy_text', '').strip() or "Leggi l'informativa completa sulla privacy"
        form.privacy_policy_new_tab = bool(request.form.get('privacy_policy_new_tab'))
        
        db.session.commit()
        flash('Form aggiornato con successo!', 'success')
        return redirect(url_for('main.list_dynamic_forms'))
    # Per la GET, mostra il form di modifica con i dati precompilati
    return render_template('dynamic_form_edit.html', form=form, dropdown_fields=dropdown_fields, dropdown_options=form.dropdown_options or {})

@main.route('/api/form/<slug>/privacy-settings', methods=['GET'])
def api_form_privacy_settings(slug):
    """API endpoint per ottenere le impostazioni privacy di un form specifico"""
    form = DynamicForm.query.filter_by(slug=slug).first_or_404()
    
    # Verifica che il form sia attivo
    now = datetime.utcnow()
    if not form.is_active or (form.active_from and now < form.active_from) or (form.active_until and now > form.active_until):
        return jsonify({'error': 'Form non disponibile'}), 404
    
    return jsonify({
        'enabled': form.privacy_policy_enabled,
        'url': form.privacy_policy_url,
        'text': form.privacy_policy_text or "Leggi l'informativa completa sulla privacy",
        'openInNewTab': form.privacy_policy_new_tab
    })

@main.route('/api/candidates', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def api_get_candidates():
    # Filtra per candidati non archiviati per default
    archived = request.args.get('archived', 'false').lower() == 'true'
    candidates = Candidate.query.options(joinedload(Candidate.form)).filter_by(archived=archived).all()
    return jsonify([
        {
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email,
            'phone_number': c.phone_number,
            'come_sei_arrivato': c.come_sei_arrivato,
            'gender': c.gender,
            'date_of_birth': c.date_of_birth.isoformat() if c.date_of_birth else '',
            'place_of_birth': c.place_of_birth,
            'nationality': c.nationality,
            'marital_status': c.marital_status,
            'height_cm': c.height_cm,
            'weight_kg': c.weight_kg,
            'tshirt_size': c.tshirt_size,
            'shoe_size_eu': c.shoe_size_eu,
            'address': c.address,
            'city': c.city,
            'postal_code': c.postal_code,
            'country_of_residence': c.country_of_residence,
            'id_document': c.id_document,
            'id_number': c.id_number,
            'id_expiry_date': c.id_expiry_date.isoformat() if c.id_expiry_date else '',
            'id_country': c.id_country,
            'license_country': c.license_country,
            'license_number': c.license_number,
            'license_category': c.license_category,
            'license_issue_date': c.license_issue_date.isoformat() if c.license_issue_date else '',
            'license_expiry_date': c.license_expiry_date.isoformat() if c.license_expiry_date else '',
            'years_driving_experience': c.years_driving_experience,
            'auto_moto_munito': c.auto_moto_munito,
            'occupation': c.occupation,
            'other_experience': c.other_experience,
            'availability_from': c.availability_from.isoformat() if c.availability_from else '',
            'availability_till': c.availability_till.isoformat() if c.availability_till else '',
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
            'form_name': c.form.name if c.form else '',
            'form_category': c.form.category if c.form else '',
            'form_subcategory': c.form.subcategory if c.form else '',
            'curriculum_file': url_for('main.serve_curriculum', filename=c.curricula[0].filename.split('/')[-1] if c.curricula[0].filename.startswith('https://') else c.curricula[0].filename) if c.curricula else '',
            'profile_photo': url_for('main.serve_photo', filename=c.photos[0].filename.split('/')[-1] if c.photos[0].filename.startswith('https://') else c.photos[0].filename) if c.photos else '',
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'total_score': round(c.get_total_score(), 1),
            'average_score': round(c.get_average_score(), 1),
            'scores_count': len(c.scores) if c.scores else 0
        } for c in candidates
    ])

@main.route('/api/filter-options', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def api_get_filter_options():
    """Restituisce le opzioni disponibili per i filtri dropdown"""
    # Query per ottenere tutti i form distinti con le loro categorie e sottocategorie
    forms_query = db.session.query(
        DynamicForm.name,
        DynamicForm.category,
        DynamicForm.subcategory
    ).distinct().all()
    
    form_names = []
    categories = []
    subcategories = []
    
    for form_name, category, subcategory in forms_query:
        if form_name and form_name not in form_names:
            form_names.append(form_name)
        if category and category not in categories:
            categories.append(category)
        if subcategory and subcategory not in subcategories:
            subcategories.append(subcategory)
    
    # Ottieni valori unici per i campi candidati
    def get_unique_values(field_name):
        """Ottiene valori unici non nulli per un campo"""
        values = db.session.query(getattr(Candidate, field_name))\
            .filter(getattr(Candidate, field_name).isnot(None))\
            .filter(getattr(Candidate, field_name) != '')\
            .distinct().all()
        return sorted([v[0] for v in values if v[0]])
    
    def get_boolean_values(field_name):
        """Ottiene i valori booleani per un campo, convertendoli in stringhe leggibili"""
        values = db.session.query(getattr(Candidate, field_name))\
            .filter(getattr(Candidate, field_name).isnot(None))\
            .distinct().all()
        
        result = []
        for v in values:
            if v[0] is True:
                result.append('Sì')
            elif v[0] is False:
                result.append('No')
        
        return sorted(list(set(result)))
    
    # Campi per cui vogliamo dropdown con valori dinamici
    dropdown_fields = {
        'gender': get_unique_values('gender'),
        'marital_status': get_unique_values('marital_status'),
        'nationality': get_unique_values('nationality'),
        'country_of_residence': get_unique_values('country_of_residence'),
        'id_document': get_unique_values('id_document'),
        'id_country': get_unique_values('id_country'),
        'license_country': get_unique_values('license_country'),
        'license_category': get_unique_values('license_category'),
        'auto_moto_munito': get_boolean_values('auto_moto_munito'),
        'occupation': get_unique_values('occupation'),
        'city_availability': get_unique_values('city_availability'),
        'language_1': get_unique_values('language_1'),
        'language_2': get_unique_values('language_2'),
        'language_3': get_unique_values('language_3'),
        'proficiency_1': get_unique_values('proficiency_1'),
        'proficiency_2': get_unique_values('proficiency_2'),
        'proficiency_3': get_unique_values('proficiency_3'),
        'tshirt_size': get_unique_values('tshirt_size'),
        'come_sei_arrivato': get_unique_values('come_sei_arrivato')
    }
    
    return jsonify({
        'form_names': sorted(form_names),
        'categories': sorted(categories),
        'subcategories': sorted(subcategories),
        'dropdown_fields': dropdown_fields
    })

@main.route('/api/candidates/<int:candidate_id>', methods=['PUT'])
@login_required
@role_required('intervistatore')
def api_update_candidate(candidate_id):
    c = Candidate.query.get_or_404(candidate_id)
    data = request.json
    c.first_name = data.get('first_name', c.first_name)
    c.last_name = data.get('last_name', c.last_name)
    c.email = data.get('email', c.email)
    c.phone_number = data.get('phone_number', c.phone_number)
    c.come_sei_arrivato = data.get('come_sei_arrivato', c.come_sei_arrivato)
    c.gender = data.get('gender', c.gender)
    c.date_of_birth = data.get('date_of_birth', c.date_of_birth)
    c.place_of_birth = data.get('place_of_birth', c.place_of_birth)
    c.nationality = data.get('nationality', c.nationality)
    c.marital_status = data.get('marital_status', c.marital_status)
    c.height_cm = data.get('height_cm', c.height_cm)
    c.weight_kg = data.get('weight_kg', c.weight_kg)
    c.tshirt_size = data.get('tshirt_size', c.tshirt_size)
    c.shoe_size_eu = data.get('shoe_size_eu', c.shoe_size_eu)
    c.address = data.get('address', c.address)
    c.city = data.get('city', c.city)
    c.postal_code = data.get('postal_code', c.postal_code)
    c.country_of_residence = data.get('country_of_residence', c.country_of_residence)
    c.id_document = data.get('id_document', c.id_document)
    c.id_number = data.get('id_number', c.id_number)
    c.id_expiry_date = data.get('id_expiry_date', c.id_expiry_date)
    c.id_country = data.get('id_country', c.id_country)
    c.license_country = data.get('license_country', c.license_country)
    c.license_number = data.get('license_number', c.license_number)
    c.license_category = data.get('license_category', c.license_category)
    c.license_issue_date = data.get('license_issue_date', c.license_issue_date)
    c.license_expiry_date = data.get('license_expiry_date', c.license_expiry_date)
    c.years_driving_experience = data.get('years_driving_experience', c.years_driving_experience)
    c.auto_moto_munito = data.get('auto_moto_munito', c.auto_moto_munito)
    c.occupation = data.get('occupation', c.occupation)
    c.other_experience = data.get('other_experience', c.other_experience)
    
    # Gestione dei nuovi campi data per availability
    availability_from = data.get('availability_from')
    if availability_from:
        try:
            c.availability_from = datetime.strptime(availability_from, '%Y-%m-%d').date()
        except:
            c.availability_from = availability_from if isinstance(availability_from, date) else None
    
    availability_till = data.get('availability_till')
    if availability_till:
        try:
            c.availability_till = datetime.strptime(availability_till, '%Y-%m-%d').date()
        except:
            c.availability_till = availability_till if isinstance(availability_till, date) else None
    
    c.city_availability = data.get('city_availability', c.city_availability)
    c.additional_document = data.get('additional_document', c.additional_document)
    c.codice_fiscale = data.get('codice_fiscale', c.codice_fiscale)
    c.permesso_soggiorno = data.get('permesso_soggiorno', c.permesso_soggiorno)
    c.language_1 = data.get('language_1', c.language_1)
    c.proficiency_1 = data.get('proficiency_1', c.proficiency_1)
    c.language_2 = data.get('language_2', c.language_2)
    c.proficiency_2 = data.get('proficiency_2', c.proficiency_2)
    c.language_3 = data.get('language_3', c.language_3)
    c.proficiency_3 = data.get('proficiency_3', c.proficiency_3)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/api/candidates/<int:candidate_id>/archive', methods=['POST'])
@login_required
@role_required('intervistatore')
def api_archive_candidate(candidate_id):
    """Archivia o desarchivia un candidato"""
    c = Candidate.query.get_or_404(candidate_id)
    data = request.json or {}
    archived = data.get('archived', True)  # Default: archivia
    
    c.archived = archived
    db.session.commit()
    
    action = "archiviato" if archived else "ripristinato"
    return jsonify({'success': True, 'message': f'Candidato {action} con successo'})

@main.route('/file/curriculum/<path:filename>')
@login_required
@view_only_required('intervistatore')
def serve_curriculum(filename):
    """Serve curriculum files attraverso URL sicuri con SAS token"""
    try:
        current_app.logger.info(f"Richiesta curriculum per: {filename}")
        
        # Se filename è già un URL completo, estrapolane solo il nome del file
        if filename.startswith('https://'):
            filename = filename.split('/')[-1]
        
        current_app.logger.info(f"Nome file estratto: {filename}")
        
        # Costruisci l'URL completo del blob
        blob_url = f"https://w3data.blob.core.windows.net/candidati-files/{filename}"
        
        # Genera URL sicuro con SAS token (più tempo per visualizzazione)
        secure_url = get_secure_document_url(blob_url)
        
        current_app.logger.info(f"URL sicuro generato: {secure_url}")
        
        if secure_url:
            # Controlla se è una richiesta per visualizzazione inline
            view_mode = request.args.get('view', 'download')
            if view_mode == 'inline':
                return redirect(secure_url)
            else:
                # Modalità download tradizionale
                return redirect(secure_url)
        else:
            return 'Errore nella generazione dell\'URL sicuro', 500
            
    except Exception as e:
        current_app.logger.error(f"Errore accesso curriculum {filename}: {str(e)}")
        return f'Errore accesso file: {str(e)}', 500

@main.route('/curriculum/view/<path:filename>')
@login_required
@view_only_required('intervistatore')
def view_curriculum_inline(filename):
    """Visualizza il curriculum in una pagina dedicata con viewer PDF integrato"""
    try:
        current_app.logger.info(f"Visualizzazione inline curriculum: {filename}")
        
        # Se filename è già un URL completo, estrapolane solo il nome del file
        if filename.startswith('https://'):
            original_filename = filename.split('/')[-1]
        else:
            original_filename = filename
        
        # Genera URL per il proxy PDF locale
        pdf_proxy_url = url_for('main.pdf_proxy', filename=original_filename)
        
        return render_template('curriculum_viewer.html', 
                             pdf_url=pdf_proxy_url, 
                             filename=original_filename)
            
    except Exception as e:
        current_app.logger.error(f"Errore visualizzazione curriculum {filename}: {str(e)}")
        flash(f'Errore visualizzazione file: {str(e)}', 'error')
        return redirect(url_for('main.candidates_list'))

@main.route('/pdf-proxy/<path:filename>')
@login_required
@view_only_required('intervistatore')
def pdf_proxy(filename):
    """Proxy che scarica il PDF dal blob storage e lo serve con header appropriati"""
    try:
        current_app.logger.info(f"Proxy PDF per: {filename}")
        
        # Costruisci l'URL completo del blob
        blob_url = f"https://w3data.blob.core.windows.net/candidati-files/{filename}"
        
        # Genera URL sicuro con SAS token
        secure_url = get_secure_document_url(blob_url, inline=False)
        
        if not secure_url:
            return 'Errore nella generazione dell\'URL sicuro', 500
        
        # Scarica il PDF dal blob storage
        response = requests.get(secure_url, timeout=30)
        
        if response.status_code != 200:
            current_app.logger.error(f"Errore download PDF: {response.status_code}")
            return f'Errore download PDF: {response.status_code}', 500
        
        # Prepara la risposta con header appropriati per visualizzazione inline
        pdf_response = Response(
            response.content,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'Content-Type': 'application/pdf',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
        current_app.logger.info(f"PDF proxy successful per {filename}")
        return pdf_response
        
    except Exception as e:
        current_app.logger.error(f"Errore PDF proxy {filename}: {str(e)}")
        return f'Errore accesso file: {str(e)}', 500

@main.route('/file/photo/<path:filename>')
@login_required  
@view_only_required('intervistatore')
def serve_photo(filename):
    """Serve photo files attraverso URL sicuri con SAS token"""
    try:
        current_app.logger.info(f"Richiesta foto per: {filename}")
        
        # Se filename è già un URL completo, estrapolane solo il nome del file
        if filename.startswith('https://'):
            filename = filename.split('/')[-1]
        
        current_app.logger.info(f"Nome file estratto: {filename}")
        
        # Costruisci l'URL completo del blob
        blob_url = f"https://w3data.blob.core.windows.net/candidati-files/{filename}"
        
        # Genera URL sicuro con SAS token (24h per le immagini)
        secure_url = get_secure_image_url(blob_url)
        
        current_app.logger.info(f"URL sicuro generato: {secure_url}")
        
        if secure_url:
            return redirect(secure_url)
        else:
            return 'Errore nella generazione dell\'URL sicuro', 500
            
    except Exception as e:
        current_app.logger.error(f"Errore accesso foto {filename}: {str(e)}")
        return f'Errore accesso file: {str(e)}', 500

@main.route('/success')
def success():
    return render_template('success.html')

# === GESTIONE PUNTEGGI ===

@main.route('/candidati/<int:candidate_id>/punteggi')
@login_required
@view_only_required('intervistatore')
def view_candidate_scores(candidate_id):
    """Visualizza i punteggi di un candidato"""
    candidate = Candidate.query.get_or_404(candidate_id)
    categories = ScoreCategory.query.filter_by(is_active=True).all()
    
    # Raggruppa i punteggi per categoria
    score_summary = candidate.get_score_summary()
    
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': url_for('main.candidates_list')},
        {'name': f'{candidate.first_name} {candidate.last_name}', 'url': url_for('main.candidate_profile', candidate_id=candidate.id)},
        {'name': 'Punteggi', 'url': None}
    ]
    
    return render_template('candidate_scores.html', 
                         candidate=candidate, 
                         categories=categories,
                         score_summary=score_summary,
                         total_score=candidate.get_total_score(),
                         average_score=candidate.get_average_score(),
                         breadcrumbs=breadcrumbs)

@main.route('/candidati/<int:candidate_id>/punteggi/aggiungi', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def add_candidate_score(candidate_id):
    """Aggiungi un punteggio a un candidato"""
    candidate = Candidate.query.get_or_404(candidate_id)
    categories = ScoreCategory.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        category = request.form.get('category')
        subcategory = request.form.get('subcategory')
        score = float(request.form.get('score', 0))
        max_score = float(request.form.get('max_score', 10))
        weight = float(request.form.get('weight', 1.0))
        notes = request.form.get('notes')
        
        # Crea nuovo punteggio
        new_score = Score(
            candidate_id=candidate_id,
            user_id=current_user.id,
            category=category,
            subcategory=subcategory,
            score=score,
            max_score=max_score,
            weight=weight,
            notes=notes
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        flash(f'Punteggio aggiunto con successo per {category}', 'success')
        return redirect(url_for('main.view_candidate_scores', candidate_id=candidate_id))
    
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': url_for('main.candidates_list')},
        {'name': f'{candidate.first_name} {candidate.last_name}', 'url': url_for('main.candidate_profile', candidate_id=candidate.id)},
        {'name': 'Punteggi', 'url': url_for('main.view_candidate_scores', candidate_id=candidate.id)},
        {'name': 'Aggiungi Punteggio', 'url': None}
    ]
    
    return render_template('add_candidate_score.html', 
                         candidate=candidate, 
                         categories=categories,
                         breadcrumbs=breadcrumbs)

@main.route('/candidati/<int:candidate_id>/punteggi/<int:score_id>/modifica', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def edit_candidate_score(candidate_id, score_id):
    """Modifica un punteggio di un candidato"""
    candidate = Candidate.query.get_or_404(candidate_id)
    score = Score.query.get_or_404(score_id)
    categories = ScoreCategory.query.filter_by(is_active=True).all()
    
    # Verifica che il punteggio appartenga al candidato
    if score.candidate_id != candidate_id:
        abort(404)
    
    if request.method == 'POST':
        score.category = request.form.get('category')
        score.subcategory = request.form.get('subcategory')
        score.score = float(request.form.get('score', 0))
        score.max_score = float(request.form.get('max_score', 10))
        score.weight = float(request.form.get('weight', 1.0))
        score.notes = request.form.get('notes')
        
        db.session.commit()
        
        flash(f'Punteggio modificato con successo per {score.category}', 'success')
        return redirect(url_for('main.view_candidate_scores', candidate_id=candidate_id))
    
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': url_for('main.candidates_list')},
        {'name': f'{candidate.first_name} {candidate.last_name}', 'url': url_for('main.candidate_profile', candidate_id=candidate.id)},
        {'name': 'Punteggi', 'url': url_for('main.view_candidate_scores', candidate_id=candidate.id)},
        {'name': 'Modifica Punteggio', 'url': None}
    ]
    
    return render_template('edit_candidate_score.html', 
                         candidate=candidate, 
                         score=score,
                         categories=categories,
                         breadcrumbs=breadcrumbs)

@main.route('/candidati/<int:candidate_id>/punteggi/<int:score_id>/elimina', methods=['POST'])
@login_required
@role_required('intervistatore')
def delete_candidate_score(candidate_id, score_id):
    """Elimina un punteggio di un candidato"""
    candidate = Candidate.query.get_or_404(candidate_id)
    score = Score.query.get_or_404(score_id)
    
    # Verifica che il punteggio appartenga al candidato
    if score.candidate_id != candidate_id:
        abort(404)
    
    db.session.delete(score)
    db.session.commit()
    
    flash(f'Punteggio per {score.category} eliminato con successo', 'success')
    return redirect(url_for('main.view_candidate_scores', candidate_id=candidate_id))

@main.route('/punteggi/categorie')
@login_required
@role_required('intervistatore')
def score_categories():
    """Gestione categorie di punteggio"""
    categories = ScoreCategory.query.all()
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Categorie Punteggio', 'url': None}
    ]
    
    return render_template('score_categories.html', categories=categories, breadcrumbs=breadcrumbs)

@main.route('/punteggi/categorie/aggiungi', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def add_score_category():
    """Aggiungi una nuova categoria di punteggio"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        max_score = float(request.form.get('max_score', 10))
        weight = float(request.form.get('weight', 1.0))
        
        # Controlla se la categoria esiste già
        existing = ScoreCategory.query.filter_by(name=name).first()
        if existing:
            flash('Una categoria con questo nome esiste già', 'danger')
            return redirect(url_for('main.add_score_category'))
        
        new_category = ScoreCategory(
            name=name,
            description=description,
            max_score=max_score,
            weight=weight
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        flash(f'Categoria "{name}" aggiunta con successo', 'success')
        return redirect(url_for('main.score_categories'))
    
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Categorie Punteggio', 'url': url_for('main.score_categories')},
        {'name': 'Aggiungi Categoria', 'url': None}
    ]
    
    return render_template('add_score_category.html', breadcrumbs=breadcrumbs)

@main.route('/punteggi/categorie/<int:category_id>/modifica', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def edit_score_category(category_id):
    """Modifica una categoria di punteggio"""
    category = ScoreCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.max_score = float(request.form.get('max_score', 10))
        category.weight = float(request.form.get('weight', 1.0))
        category.is_active = bool(request.form.get('is_active'))
        
        db.session.commit()
        
        flash(f'Categoria "{category.name}" modificata con successo', 'success')
        return redirect(url_for('main.score_categories'))
    
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Categorie Punteggio', 'url': url_for('main.score_categories')},
        {'name': f'Modifica {category.name}', 'url': None}
    ]
    
    return render_template('edit_score_category.html', category=category, breadcrumbs=breadcrumbs)

@main.route('/punteggi/categorie/<int:category_id>/elimina', methods=['POST'])
@login_required
@role_required('intervistatore')
def delete_score_category(category_id):
    """Elimina una categoria di punteggio"""
    category = ScoreCategory.query.get_or_404(category_id)
    
    # Controlla se ci sono punteggi associati
    existing_scores = Score.query.filter_by(category=category.name).first()
    if existing_scores:
        flash('Impossibile eliminare la categoria: ci sono punteggi associati', 'danger')
        return redirect(url_for('main.score_categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Categoria "{category.name}" eliminata con successo', 'success')
    return redirect(url_for('main.score_categories'))

# === API ENDPOINTS PER PUNTEGGI ===

@main.route('/api/candidates/<int:candidate_id>/scores', methods=['GET'])
@login_required
def api_get_candidate_scores(candidate_id):
    """API per ottenere i punteggi di un candidato"""
    candidate = Candidate.query.get_or_404(candidate_id)
    
    scores_data = []
    for score in candidate.scores:
        scores_data.append({
            'id': score.id,
            'category': score.category,
            'subcategory': score.subcategory,
            'score': score.score,
            'max_score': score.max_score,
            'percentage': score.percentage,
            'weight': score.weight,
            'weighted_score': score.weighted_score,
            'notes': score.notes,
            'evaluator': score.evaluator.username if score.evaluator else None,
            'created_at': score.created_at.isoformat(),
            'updated_at': score.updated_at.isoformat()
        })
    
    return jsonify({
        'candidate_id': candidate_id,
        'scores': scores_data,
        'total_score': candidate.get_total_score(),
        'average_score': candidate.get_average_score(),
        'score_summary': candidate.get_score_summary()
    })

@main.route('/candidati/<int:candidate_id>/profilo')
@login_required
@view_only_required('intervistatore')
def candidate_profile(candidate_id):
    """Visualizza il profilo completo del candidato"""
    candidate = Candidate.query.options(
        joinedload(Candidate.form),
        joinedload(Candidate.scores).joinedload(Score.evaluator)
    ).get_or_404(candidate_id)
    
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Elenco Candidati', 'url': url_for('main.candidates_list')},
        {'name': f'{candidate.first_name} {candidate.last_name}', 'url': None}
    ]
    
    return render_template('candidate_profile.html', candidate=candidate, breadcrumbs=breadcrumbs)

@main.route('/api/candidates/<int:candidate_id>/scores', methods=['POST'])
@login_required
@role_required('intervistatore')
def api_add_candidate_score(candidate_id):
    """API per aggiungere un punteggio a un candidato"""
    candidate = Candidate.query.get_or_404(candidate_id)
    
    data = request.get_json()
    
    new_score = Score(
        candidate_id=candidate_id,
        user_id=current_user.id,
        category=data.get('category'),
        subcategory=data.get('subcategory'),
        score=float(data.get('score', 0)),
        max_score=float(data.get('max_score', 10)),
        weight=float(data.get('weight', 1.0)),
        notes=data.get('notes')
    )
    
    db.session.add(new_score)
    db.session.commit()
    
    return jsonify({
        'message': 'Punteggio aggiunto con successo',
        'score_id': new_score.id
    }), 201

@main.route('/candidati/<int:candidate_id>/export/pdf')
@login_required
@view_only_required('intervistatore')
def export_candidate_pdf(candidate_id):
    """Esporta il profilo del candidato in formato PDF"""
    try:
        candidate = Candidate.query.options(
            joinedload(Candidate.form),
            joinedload(Candidate.scores).joinedload(Score.evaluator)
        ).get_or_404(candidate_id)
        
        # Genera HTML per il PDF
        html_content = render_template('candidate_pdf_export.html', 
                                     candidate=candidate, 
                                     export_date=datetime.now())
        
        try:
            # Prova a usare xhtml2pdf per generare il PDF
            from xhtml2pdf import pisa
            
            # Crea buffer per il PDF
            pdf_buffer = BytesIO()
            
            # Converti HTML in PDF
            pisa_status = pisa.CreatePDF(html_content.encode('utf-8'), dest=pdf_buffer, encoding='utf-8')
            
            if pisa_status.err:
                # Se fallisce, ritorna HTML come fallback
                current_app.logger.warning("Errore generazione PDF, fallback a HTML")
                response = make_response(html_content)
                response.headers['Content-Type'] = 'text/html'
                response.headers['Content-Disposition'] = f'inline; filename="profilo_{candidate.first_name}_{candidate.last_name}.html"'
                return response
            
            # PDF generato con successo
            pdf_buffer.seek(0)
            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="profilo_{candidate.first_name}_{candidate.last_name}.pdf"'
            
            return response
            
        except ImportError:
            # Se xhtml2pdf non è disponibile, fallback a HTML
            current_app.logger.warning("xhtml2pdf non disponibile, fallback a HTML")
            response = make_response(html_content)
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = f'inline; filename="profilo_{candidate.first_name}_{candidate.last_name}.html"'
            return response
        
    except Exception as e:
        current_app.logger.error(f"Errore esportazione PDF candidato {candidate_id}: {str(e)}")
        flash('Errore durante l\'esportazione PDF', 'error')
        return redirect(url_for('main.candidate_profile', candidate_id=candidate_id))

@main.route('/candidati/<int:candidate_id>/export/print')
@login_required
@view_only_required('intervistatore')
def export_candidate_print(candidate_id):
    """Mostra la pagina di stampa del profilo candidato con dialog automatico"""
    try:
        candidate = Candidate.query.options(
            joinedload(Candidate.form),
            joinedload(Candidate.scores).joinedload(Score.evaluator)
        ).get_or_404(candidate_id)
        
        # Usa il template con JavaScript per aprire il dialog di stampa
        return render_template('candidate_print_export.html', 
                             candidate=candidate, 
                             export_date=datetime.now())
        
    except Exception as e:
        current_app.logger.error(f"Errore pagina stampa candidato {candidate_id}: {str(e)}")
        flash('Errore durante l\'apertura della pagina di stampa', 'error')
        return redirect(url_for('main.candidate_profile', candidate_id=candidate_id))

@main.route('/candidati/<int:candidate_id>/export/csv')
@login_required
@view_only_required('intervistatore')
def export_candidate_csv(candidate_id):
    """Esporta il profilo del candidato in formato CSV"""
    try:
        candidate = Candidate.query.options(
            joinedload(Candidate.form),
            joinedload(Candidate.scores).joinedload(Score.evaluator)
        ).get_or_404(candidate_id)
        
        # Prepara i dati CSV
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header CSV
        writer.writerow(['Campo', 'Valore'])
        
        # Dati anagrafici
        writer.writerow(['Nome', candidate.first_name or ''])
        writer.writerow(['Cognome', candidate.last_name or ''])
        writer.writerow(['Email', candidate.email or ''])
        writer.writerow(['Telefono', candidate.phone_number or ''])
        writer.writerow(['Genere', candidate.gender or ''])
        writer.writerow(['Data di nascita', candidate.date_of_birth.strftime('%d/%m/%Y') if candidate.date_of_birth else ''])
        writer.writerow(['Luogo di nascita', candidate.place_of_birth or ''])
        writer.writerow(['Nazionalità', candidate.nationality or ''])
        writer.writerow(['Stato civile', candidate.marital_status or ''])
        writer.writerow(['Come sei arrivato', candidate.come_sei_arrivato or ''])
        
        # Dati fisici
        writer.writerow(['Altezza (cm)', candidate.height_cm or ''])
        writer.writerow(['Peso (kg)', candidate.weight_kg or ''])
        writer.writerow(['Taglia T-shirt', candidate.tshirt_size or ''])
        writer.writerow(['Numero scarpe', candidate.shoe_size_eu or ''])
        
        # Indirizzo
        writer.writerow(['Indirizzo', candidate.address or ''])
        writer.writerow(['Città', candidate.city or ''])
        writer.writerow(['CAP', candidate.postal_code or ''])
        writer.writerow(['Paese di residenza', candidate.country_of_residence or ''])
        
        # Documenti
        writer.writerow(['Tipo documento', candidate.id_document or ''])
        writer.writerow(['Numero documento', candidate.id_number or ''])
        writer.writerow(['Scadenza documento', candidate.id_expiry_date.strftime('%d/%m/%Y') if candidate.id_expiry_date else ''])
        writer.writerow(['Paese documento', candidate.id_country or ''])
        writer.writerow(['Codice fiscale', candidate.codice_fiscale or ''])
        writer.writerow(['Permesso soggiorno', candidate.permesso_soggiorno or ''])
        
        # Patente
        writer.writerow(['Paese patente', candidate.license_country or ''])
        writer.writerow(['Numero patente', candidate.license_number or ''])
        writer.writerow(['Categoria patente', candidate.license_category or ''])
        writer.writerow(['Data rilascio patente', candidate.license_issue_date.strftime('%d/%m/%Y') if candidate.license_issue_date else ''])
        writer.writerow(['Scadenza patente', candidate.license_expiry_date.strftime('%d/%m/%Y') if candidate.license_expiry_date else ''])
        writer.writerow(['Anni esperienza guida', candidate.years_driving_experience or ''])
        writer.writerow(['Auto/Moto munito', candidate.auto_moto_munito or ''])
        
        # Lingue
        writer.writerow(['Lingua 1', candidate.language_1 or ''])
        writer.writerow(['Livello lingua 1', candidate.proficiency_1 or ''])
        writer.writerow(['Lingua 2', candidate.language_2 or ''])
        writer.writerow(['Livello lingua 2', candidate.proficiency_2 or ''])
        writer.writerow(['Lingua 3', candidate.language_3 or ''])
        writer.writerow(['Livello lingua 3', candidate.proficiency_3 or ''])
        
        # Lavoro
        writer.writerow(['Occupazione', candidate.occupation or ''])
        writer.writerow(['Città disponibilità', candidate.city_availability or ''])
        writer.writerow(['Disponibile da', candidate.availability_from.strftime('%d/%m/%Y') if candidate.availability_from else ''])
        writer.writerow(['Disponibile fino', candidate.availability_till.strftime('%d/%m/%Y') if candidate.availability_till else ''])
        writer.writerow(['Altre esperienze', candidate.other_experience or ''])
        
        # Form associato
        if candidate.form:
            writer.writerow(['Form compilato', candidate.form.name])
            writer.writerow(['Categoria form', candidate.form.category or ''])
            writer.writerow(['Sottocategoria form', candidate.form.subcategory or ''])
        
        # Punteggi
        writer.writerow(['', ''])  # Riga vuota
        writer.writerow(['=== PUNTEGGI ===', ''])
        
        if candidate.scores:
            writer.writerow(['Punteggio totale', f"{candidate.get_total_score():.1f}"])
            writer.writerow(['Media punteggi', f"{candidate.get_average_score():.1f}"])
            writer.writerow(['Numero valutazioni', len(candidate.scores)])
            writer.writerow(['', ''])  # Riga vuota
            
            writer.writerow(['Categoria', 'Sottocategoria', 'Punteggio', 'Max', 'Percentuale', 'Peso', 'Valutatore', 'Data', 'Note'])
            for score in candidate.scores:
                writer.writerow([
                    score.category,
                    score.subcategory or '',
                    score.score,
                    score.max_score,
                    f"{score.percentage:.1f}%",
                    score.weight,
                    score.evaluator.username if score.evaluator else '',
                    score.created_at.strftime('%d/%m/%Y'),
                    score.notes or ''
                ])
        else:
            writer.writerow(['Nessun punteggio presente', ''])
        
        # Prepara la risposta
        csv_content = output.getvalue()
        output.close()
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="profilo_{candidate.first_name}_{candidate.last_name}.csv"'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Errore esportazione CSV candidato {candidate_id}: {str(e)}")
        flash('Errore durante l\'esportazione CSV', 'error')
        return redirect(url_for('main.candidate_profile', candidate_id=candidate_id))


@main.route('/debug/user-info')
@login_required
def debug_user_info():
    """Route di debug per controllare le informazioni utente"""
    return f"<h1>User Info</h1><p>Username: {current_user.username}</p><p>Role: {current_user.role}</p><p>ID: {current_user.id}</p>"


@main.route('/candidati/export/csv', methods=['POST'])
@login_required
def export_candidates_csv():
    """Esporta l'elenco dei candidati in formato CSV con campi selezionabili"""
    try:
        # Ottieni i campi selezionati dalla richiesta
        selected_fields = request.form.getlist('fields')
        export_type = request.form.get('export_type', 'all')  # 'all' o 'filtered'
        
        if not selected_fields:
            flash('Nessun campo selezionato per l\'esportazione', 'error')
            return redirect(url_for('main.candidates_list'))
        
        # Mappa dei campi con le relative etichette - CORRETTI per il modello Candidate
        field_labels = {
            'name': 'Nome',  # first_name
            'surname': 'Cognome',  # last_name
            'birth_date': 'Data di Nascita',  # date_of_birth
            'birth_place': 'Luogo di Nascita',  # place_of_birth
            'nationality': 'Nazionalità',  # nationality
            'residence': 'Residenza',  # address + city
            'email': 'Email',  # email
            'phone': 'Telefono',  # phone_number
            'gender': 'Genere',  # gender
            'marital_status': 'Stato Civile',  # marital_status
            'codice_fiscale': 'Codice Fiscale',  # codice_fiscale
            'occupation': 'Occupazione',  # occupation
            'city_availability': 'Città Disponibilità',  # city_availability
            'come_sei_arrivato': 'Come sei arrivato',  # come_sei_arrivato
            'archived': 'Archiviato',  # archived
            'created_at': 'Data di Creazione',  # created_at
            'form_name': 'Nome Form',  # tramite relazione form
            'total_score': 'Punteggio Totale',
        }
        
        # Ottieni candidati in base al tipo di esportazione
        if export_type == 'filtered':
            # Se è richiesta l'esportazione filtrata, ottieni gli ID dalla richiesta
            candidate_ids = request.form.getlist('candidate_ids')
            if candidate_ids:
                # Converte gli ID da string a int
                candidate_ids = [int(id_str) for id_str in candidate_ids if id_str.isdigit()]
                candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
            else:
                candidates = []
        else:
            # Esportazione di tutti i candidati
            archived = request.form.get('archived', 'false').lower() == 'true'
            candidates = Candidate.query.filter_by(archived=archived).all()
        
        # Crea il file CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Scrivi l'header con i campi selezionati
        header = [field_labels.get(field, field) for field in selected_fields]
        writer.writerow(header)
        
        # Scrivi i dati dei candidati
        for candidate in candidates:
            row = []
            for field in selected_fields:
                if field == 'name':
                    row.append(candidate.first_name or '')
                elif field == 'surname':
                    row.append(candidate.last_name or '')
                elif field == 'birth_date':
                    row.append(candidate.date_of_birth.strftime('%d/%m/%Y') if candidate.date_of_birth else '')
                elif field == 'birth_place':
                    row.append(candidate.place_of_birth or '')
                elif field == 'nationality':
                    row.append(candidate.nationality or '')
                elif field == 'residence':
                    address_parts = []
                    if candidate.address:
                        address_parts.append(candidate.address)
                    if candidate.city:
                        address_parts.append(candidate.city)
                    row.append(', '.join(address_parts))
                elif field == 'email':
                    row.append(candidate.email or '')
                elif field == 'phone':
                    row.append(candidate.phone_number or '')
                elif field == 'gender':
                    row.append(candidate.gender or '')
                elif field == 'marital_status':
                    row.append(candidate.marital_status or '')
                elif field == 'codice_fiscale':
                    row.append(candidate.codice_fiscale or '')
                elif field == 'occupation':
                    row.append(candidate.occupation or '')
                elif field == 'city_availability':
                    row.append(candidate.city_availability or '')
                elif field == 'come_sei_arrivato':
                    row.append(candidate.come_sei_arrivato or '')
                elif field == 'archived':
                    row.append('Sì' if candidate.archived else 'No')
                elif field == 'created_at':
                    row.append(candidate.created_at.strftime('%d/%m/%Y %H:%M') if candidate.created_at else '')
                elif field == 'form_name':
                    row.append(candidate.form.name if candidate.form else '')
                elif field == 'total_score':
                    row.append(f"{candidate.get_total_score():.1f}")
                else:
                    row.append('')
            
            writer.writerow(row)
        
        # Prepara la risposta
        csv_content = output.getvalue()
        output.close()
        
        # Genera il nome del file con timestamp e tipo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_label = 'filtrati' if export_type == 'filtered' else 'completa'
        filename = f'candidati_{export_label}_{timestamp}.csv'
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Errore esportazione CSV candidati: {str(e)}")
        flash('Errore durante l\'esportazione CSV', 'error')
        return redirect(url_for('main.candidates_list'))


@main.route('/candidati/export/pdf', methods=['POST'])
@login_required
def export_candidates_pdf():
    """Esporta l'elenco dei candidati in formato PDF con campi selezionabili"""
    try:
        # Ottieni i campi selezionati dalla richiesta
        selected_fields = request.form.getlist('fields')
        export_type = request.form.get('export_type', 'all')  # 'all' o 'filtered'
        
        if not selected_fields:
            flash('Nessun campo selezionato per l\'esportazione', 'error')
            return redirect(url_for('main.candidates_list'))
        
        # Mappa dei campi con le relative etichette - CORRETTI per il modello Candidate
        field_labels = {
            'name': 'Nome',  # first_name
            'surname': 'Cognome',  # last_name
            'birth_date': 'Data di Nascita',  # date_of_birth
            'birth_place': 'Luogo di Nascita',  # place_of_birth
            'nationality': 'Nazionalità',  # nationality
            'residence': 'Residenza',  # address + city
            'email': 'Email',  # email
            'phone': 'Telefono',  # phone_number
            'gender': 'Genere',  # gender
            'marital_status': 'Stato Civile',  # marital_status
            'codice_fiscale': 'Codice Fiscale',  # codice_fiscale
            'occupation': 'Occupazione',  # occupation
            'city_availability': 'Città Disponibilità',  # city_availability
            'come_sei_arrivato': 'Come sei arrivato',  # come_sei_arrivato
            'archived': 'Archiviato',  # archived
            'created_at': 'Data di Creazione',  # created_at
            'form_name': 'Nome Form',  # tramite relazione form
            'total_score': 'Punteggio Totale',
        }
        
        # Ottieni candidati in base al tipo di esportazione
        if export_type == 'filtered':
            # Se è richiesta l'esportazione filtrata, ottieni gli ID dalla richiesta
            candidate_ids = request.form.getlist('candidate_ids')
            if candidate_ids:
                # Converte gli ID da string a int
                candidate_ids = [int(id_str) for id_str in candidate_ids if id_str.isdigit()]
                candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
            else:
                candidates = []
        else:
            # Esportazione di tutti i candidati
            archived = request.form.get('archived', 'false').lower() == 'true'
            candidates = Candidate.query.filter_by(archived=archived).all()
        
        # Prepara i dati per il template
        candidates_data = []
        for candidate in candidates:
            candidate_data = {}
            for field in selected_fields:
                if field == 'name':
                    candidate_data[field] = candidate.first_name or ''
                elif field == 'surname':
                    candidate_data[field] = candidate.last_name or ''
                elif field == 'birth_date':
                    candidate_data[field] = candidate.date_of_birth.strftime('%d/%m/%Y') if candidate.date_of_birth else ''
                elif field == 'birth_place':
                    candidate_data[field] = candidate.place_of_birth or ''
                elif field == 'nationality':
                    candidate_data[field] = candidate.nationality or ''
                elif field == 'residence':
                    address_parts = []
                    if candidate.address:
                        address_parts.append(candidate.address)
                    if candidate.city:
                        address_parts.append(candidate.city)
                    candidate_data[field] = ', '.join(address_parts)
                elif field == 'email':
                    candidate_data[field] = candidate.email or ''
                elif field == 'phone':
                    candidate_data[field] = candidate.phone_number or ''
                elif field == 'gender':
                    candidate_data[field] = candidate.gender or ''
                elif field == 'marital_status':
                    candidate_data[field] = candidate.marital_status or ''
                elif field == 'codice_fiscale':
                    candidate_data[field] = candidate.codice_fiscale or ''
                elif field == 'occupation':
                    candidate_data[field] = candidate.occupation or ''
                elif field == 'city_availability':
                    candidate_data[field] = candidate.city_availability or ''
                elif field == 'come_sei_arrivato':
                    candidate_data[field] = candidate.come_sei_arrivato or ''
                elif field == 'archived':
                    candidate_data[field] = 'Sì' if candidate.archived else 'No'
                elif field == 'created_at':
                    candidate_data[field] = candidate.created_at.strftime('%d/%m/%Y %H:%M') if candidate.created_at else ''
                elif field == 'form_name':
                    candidate_data[field] = candidate.form.name if candidate.form else ''
                elif field == 'total_score':
                    candidate_data[field] = f"{candidate.get_total_score():.1f}"
                else:
                    candidate_data[field] = ''
            
            candidates_data.append(candidate_data)
        
        # Prova a generare il PDF con xhtml2pdf
        try:
            from xhtml2pdf import pisa
            
            # Renderizza il template HTML
            html_content = render_template('candidates_bulk_export.html',
                                         candidates=candidates_data,
                                         selected_fields=selected_fields,
                                         field_labels=field_labels,
                                         export_date=datetime.now().strftime('%d/%m/%Y %H:%M'))
            
            # Converti HTML in PDF
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
            
            if not pisa_status.err:
                pdf_buffer.seek(0)
                
                # Genera il nome del file con timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'candidati_export_{timestamp}.pdf'
                
                response = make_response(pdf_buffer.read())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                return response
            else:
                raise Exception("Errore nella generazione PDF con xhtml2pdf")
                
        except ImportError:
            current_app.logger.warning("xhtml2pdf non disponibile, uso fallback browser print")
        except Exception as e:
            current_app.logger.warning(f"Errore xhtml2pdf: {str(e)}, uso fallback browser print")
        
        # Fallback: reindirizza a una pagina ottimizzata per la stampa
        return render_template('candidates_bulk_print.html',
                             candidates=candidates_data,
                             selected_fields=selected_fields,
                             field_labels=field_labels,
                             export_date=datetime.now().strftime('%d/%m/%Y %H:%M'))
        
    except Exception as e:
        current_app.logger.error(f"Errore esportazione PDF candidati: {str(e)}")
        flash('Errore durante l\'esportazione PDF', 'error')
        return redirect(url_for('main.candidates_list'))

@main.route('/test-filtri')
def test_filtri():
    """Route di test per verificare i filtri"""
    return render_template('test_filtri.html')

# API per le statistiche della dashboard
@main.route('/api/stats/summary', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_summary():
    """API per le statistiche principali della dashboard"""
    try:
        # Applica i filtri se presenti
        query = Candidate.query
        
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        
        # Calcola statistiche
        total = len(candidates)
        
        # Calcola candidati disponibili (non archiviati e con disponibilità valida)
        from datetime import date
        today = date.today()
        
        available_count = 0
        archived_count = 0
        
        for c in candidates:
            # Conta archiviati
            if c.archived:
                archived_count += 1
                continue
            
            # Determina se è disponibile
            is_available = True
            
            # Se non ha date di disponibilità, considera disponibile
            if not c.availability_from and not c.availability_till:
                is_available = True
            # Se ha solo availability_from, controlla che sia passata o oggi
            elif c.availability_from and not c.availability_till:
                is_available = c.availability_from <= today
            # Se ha solo availability_till, controlla che sia futura o oggi
            elif not c.availability_from and c.availability_till:
                is_available = c.availability_till >= today
            # Se ha entrambe le date, controlla che oggi sia nel range
            elif c.availability_from and c.availability_till:
                is_available = c.availability_from <= today <= c.availability_till
            
            if is_available:
                available_count += 1
        
        return jsonify({
            'total': total,
            'available': available_count,
            'archived': archived_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Errore API stats summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/stats/eventi', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_eventi():
    """API per la lista degli eventi (categorie) per i filtri"""
    try:
        eventi = db.session.query(DynamicForm.category).distinct().filter(
            DynamicForm.category.isnot(None)
        ).all()
        return jsonify([evento[0] for evento in eventi if evento[0]])
    except Exception as e:
        current_app.logger.error(f"Errore API stats eventi: {str(e)}")
        return jsonify([])

@main.route('/api/stats/aziende', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_aziende():
    """API per la lista delle aziende (sottocategorie) per i filtri"""
    try:
        aziende = db.session.query(DynamicForm.subcategory).distinct().filter(
            DynamicForm.subcategory.isnot(None)
        ).all()
        return jsonify([azienda[0] for azienda in aziende if azienda[0]])
    except Exception as e:
        current_app.logger.error(f"Errore API stats aziende: {str(e)}")
        return jsonify([])

# API placeholder per i grafici della dashboard
@main.route('/api/stats/roles', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_roles():
    """API per statistiche ruoli/occupazioni"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        roles = {}
        for c in candidates:
            role = c.occupation or 'Non specificato'
            roles[role] = roles.get(role, 0) + 1
        
        return jsonify(roles)
    except Exception as e:
        return jsonify({'Non specificato': 0})

@main.route('/api/stats/gender', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_gender():
    """API per statistiche genere"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        gender = {}
        for c in candidates:
            g = c.gender or 'Non specificato'
            gender[g] = gender.get(g, 0) + 1
        
        return jsonify(gender)
    except Exception as e:
        return jsonify({'Non specificato': 0})

@main.route('/api/stats/marital_status', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_marital_status():
    """API per statistiche stato civile"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        marital = {}
        for c in candidates:
            status = c.marital_status or 'Non specificato'
            marital[status] = marital.get(status, 0) + 1
        
        return jsonify(marital)
    except Exception as e:
        return jsonify({'Non specificato': 0})

@main.route('/api/stats/tshirt_size', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_tshirt_size():
    """API per statistiche taglia t-shirt"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        sizes = {}
        for c in candidates:
            size = c.tshirt_size or 'Non specificato'
            sizes[size] = sizes.get(size, 0) + 1
        
        return jsonify(sizes)
    except Exception as e:
        return jsonify({'Non specificato': 0})

@main.route('/api/stats/auto_moto_munito', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_auto_moto():
    """API per statistiche auto/moto"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        auto = {'Sì': 0, 'No': 0, 'Non specificato': 0}
        for c in candidates:
            if c.auto_moto_munito is True:
                auto['Sì'] += 1
            elif c.auto_moto_munito is False:
                auto['No'] += 1
            else:
                auto['Non specificato'] += 1
        
        return jsonify(auto)
    except Exception as e:
        return jsonify({'Non specificato': 0})

@main.route('/api/stats/monthly', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_monthly():
    """API per statistiche mensili"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        monthly = {}
        for c in candidates:
            if c.created_at:
                month_key = c.created_at.strftime('%Y-%m')
                monthly[month_key] = monthly.get(month_key, 0) + 1
        
        return jsonify(monthly)
    except Exception as e:
        return jsonify({})

@main.route('/api/stats/cities', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_cities():
    """API per statistiche città"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.all()
        cities = {}
        for c in candidates:
            city = c.city or 'Non specificato'
            cities[city] = cities.get(city, 0) + 1
        
        # Restituisci solo le top 10 città
        sorted_cities = dict(sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10])
        return jsonify(sorted_cities)
    except Exception as e:
        return jsonify({'Non specificato': 0})

@main.route('/api/stats/latest', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_latest():
    """API per ultimi candidati inseriti"""
    try:
        query = Candidate.query
        evento = request.args.get('evento')
        azienda = request.args.get('azienda')
        
        if evento:
            query = query.filter(Candidate.form.has(DynamicForm.category == evento))
        if azienda:
            query = query.filter(Candidate.form.has(DynamicForm.subcategory == azienda))
        
        candidates = query.order_by(Candidate.created_at.desc()).limit(5).all()
        
        result = []
        for c in candidates:
            result.append({
                'first_name': c.first_name,
                'last_name': c.last_name,
                'email': c.email,
                'role': c.occupation,
                'city': c.city,
                'gender': c.gender,
                'created_at': c.created_at.strftime('%d/%m/%Y') if c.created_at else ''
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify([])

@main.route('/api/stats/license_category', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_license_category():
    """API per le statistiche delle tipologie di patente"""
    try:
        evento_id = request.args.get('evento')
        azienda_id = request.args.get('azienda')
        
        query = Candidate.query
        
        if evento_id:
            query = query.filter(Candidate.event_id == evento_id)
        if azienda_id:
            query = query.filter(Candidate.company_id == azienda_id)
        
        candidates = query.all()
        
        # Conta le categorie di patente
        license_counts = {}
        for candidate in candidates:
            if candidate.license_category:
                category = candidate.license_category.strip()
                if category:
                    license_counts[category] = license_counts.get(category, 0) + 1
        
        # Se non ci sono dati, restituisci un messaggio appropriato
        if not license_counts:
            license_counts = {'Nessun dato disponibile': 1}
        
        return jsonify(license_counts)
    except Exception as e:
        print(f"Errore in stats_license_category: {e}")
        return jsonify({'Errore': 1})

@main.route('/api/stats/languages', methods=['GET'])
@login_required
@view_only_required('intervistatore')
def stats_languages():
    """API per le statistiche delle lingue parlate"""
    try:
        evento_id = request.args.get('evento')
        azienda_id = request.args.get('azienda')
        
        query = Candidate.query
        
        if evento_id:
            query = query.filter(Candidate.event_id == evento_id)
        if azienda_id:
            query = query.filter(Candidate.company_id == azienda_id)
        
        candidates = query.all()
        
        # Conta tutte le lingue (da language_1, language_2, language_3)
        language_counts = {}
        for candidate in candidates:
            languages = [candidate.language_1, candidate.language_2, candidate.language_3]
            for lang in languages:
                if lang and lang.strip():
                    lang_clean = lang.strip()
                    language_counts[lang_clean] = language_counts.get(lang_clean, 0) + 1
        
        # Se non ci sono dati, restituisci un messaggio appropriato
        if not language_counts:
            language_counts = {'Nessun dato disponibile': 1}
        
        return jsonify(language_counts)
    except Exception as e:
        print(f"Errore in stats_languages: {e}")
        return jsonify({'Errore': 1})

# === GESTIONE UTENTI ===

@main.route('/gestione-utenti')
@login_required
@developer_required
def user_management():
    """Pagina principale per la gestione utenti"""
    users = User.query.all()
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Gestione Utenti', 'url': None}
    ]
    return render_template('user_management.html', users=users, breadcrumbs=breadcrumbs)

@main.route('/api/users', methods=['GET'])
@login_required
@developer_required
def api_get_users():
    """API per ottenere la lista degli utenti"""
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else 'N/A'
        })
    return jsonify(users_data)

@main.route('/api/users', methods=['POST'])
@login_required
@developer_required
def api_create_user():
    """API per creare un nuovo utente"""
    try:
        data = request.get_json()
        
        # Validazione
        if not data.get('username'):
            return jsonify({'error': 'Username richiesto'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email richiesta'}), 400
        if not data.get('password'):
            return jsonify({'error': 'Password richiesta'}), 400
        if not data.get('role'):
            return jsonify({'error': 'Ruolo richiesto'}), 400
        
        # Controlla se l'username esiste già
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'Username già esistente'}), 400
            
        # Controlla se l'email esiste già
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email già esistente'}), 400
        
        # Validazione ruolo
        valid_roles = ['developer', 'intervistatore', 'ospite']
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Ruolo non valido. Ruoli disponibili: {", ".join(valid_roles)}'}), 400
        
        # Crea nuovo utente
        new_user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data['role']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': f'Utente {data["username"]} creato con successo',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'role': new_user.role,
                'created_at': new_user.created_at.strftime('%d/%m/%Y %H:%M')
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Errore durante la creazione dell\'utente: {str(e)}'}), 500

@main.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@developer_required
def api_update_user(user_id):
    """API per aggiornare un utente"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Non permettere di modificare se stesso se si sta cambiando il ruolo da developer
        if user.id == current_user.id and data.get('role') != 'developer':
            return jsonify({'error': 'Non puoi rimuovere i tuoi privilegi di developer'}), 400
        
        # Aggiorna username se fornito
        if 'username' in data and data['username']:
            # Controlla se il nuovo username è già in uso
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Username già esistente'}), 400
            user.username = data['username']
        
        # Aggiorna email se fornita
        if 'email' in data and data['email']:
            # Controlla se la nuova email è già in uso
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email già esistente'}), 400
            user.email = data['email']
        
        # Aggiorna nome se fornito
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        # Aggiorna cognome se fornito
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        # Aggiorna password se fornita
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Aggiorna ruolo se fornito
        if 'role' in data and data['role']:
            valid_roles = ['developer', 'intervistatore', 'ospite']
            if data['role'] not in valid_roles:
                return jsonify({'error': f'Ruolo non valido. Ruoli disponibili: {", ".join(valid_roles)}'}), 400
            user.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'message': f'Utente {user.username} aggiornato con successo',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else 'N/A'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Errore durante l\'aggiornamento dell\'utente: {str(e)}'}), 500

@main.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@developer_required
def api_delete_user(user_id):
    """API per eliminare un utente"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Non permettere di eliminare se stesso
        if user.id == current_user.id:
            return jsonify({'error': 'Non puoi eliminare il tuo account'}), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': f'Utente {username} eliminato con successo'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Errore durante l\'eliminazione dell\'utente: {str(e)}'}), 500


# === PANNELLO CONTROLLO SVILUPPATORI ===

@main.route('/developer-panel')
@login_required
@developer_required
def developer_panel():
    """Pannello di controllo per sviluppatori - gestione impostazioni globali del sistema"""
    from .models import SystemSettings
    
    try:
        # Recupera le impostazioni correnti con conversione esplicita
        test_mode_raw = SystemSettings.get_setting('global_form_test_mode', False)
        
        # Conversione esplicita a booleano
        if isinstance(test_mode_raw, str):
            test_mode = test_mode_raw.lower() in ('true', '1', 'yes', 'on')
        else:
            test_mode = bool(test_mode_raw)
            
        print(f"DEBUG: test_mode convertito = {test_mode} (tipo: {type(test_mode)})")
    except Exception as e:
        print(f"DEBUG: Errore recupero test_mode: {e}")
        test_mode = False
    
    return render_template('developer_panel.html', 
                         title='Pannello Sviluppatore',
                         test_mode=test_mode)


@main.route('/api/developer/settings', methods=['GET'])
@login_required
@developer_required
def get_developer_settings():
    """API per recuperare le impostazioni di sistema per sviluppatori"""
    from .models import SystemSettings
    
    try:
        settings = {
            'global_form_test_mode': SystemSettings.get_setting('global_form_test_mode', False),
            'system_maintenance_mode': SystemSettings.get_setting('system_maintenance_mode', False),
            'debug_mode': SystemSettings.get_setting('debug_mode', False)
        }
        
        return jsonify(settings)
        
    except Exception as e:
        return jsonify({'error': f'Errore nel recupero delle impostazioni: {str(e)}'}), 500


@main.route('/api/developer/settings', methods=['POST'])
@login_required
@developer_required
def update_developer_settings():
    """API per aggiornare le impostazioni di sistema per sviluppatori"""
    from .models import SystemSettings
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dati non forniti'}), 400
        
        # Aggiorna le impostazioni specificate
        updated_settings = []
        
        if 'global_form_test_mode' in data:
            SystemSettings.set_setting('global_form_test_mode', data['global_form_test_mode'], 
                                     'boolean', category='system', user_id=current_user.id)
            updated_settings.append('global_form_test_mode')
        
        if 'system_maintenance_mode' in data:
            SystemSettings.set_setting('system_maintenance_mode', data['system_maintenance_mode'], 
                                     'boolean', category='system', user_id=current_user.id)
            updated_settings.append('system_maintenance_mode')
        
        if 'debug_mode' in data:
            SystemSettings.set_setting('debug_mode', data['debug_mode'], 
                                     'boolean', category='system', user_id=current_user.id)
            updated_settings.append('debug_mode')
        
        return jsonify({
            'message': f'Impostazioni aggiornate: {", ".join(updated_settings)}',
            'updated': updated_settings
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Errore nell\'aggiornamento delle impostazioni: {str(e)}'}), 500


@main.route('/api/developer/test-mode/toggle', methods=['POST'])
@login_required
@developer_required
def toggle_test_mode():
    """API per attivare/disattivare la modalità test globale dei form"""
    from .models import SystemSettings
    
    try:
        # Recupera lo stato corrente
        current_state = SystemSettings.get_setting('global_form_test_mode', False)
        new_state = not current_state
        print(f"DEBUG: Toggle test mode - current: {current_state}, new: {new_state}")
        
        # Aggiorna l'impostazione
        SystemSettings.set_setting('global_form_test_mode', new_state, 'boolean', category='system', user_id=current_user.id)
        print(f"DEBUG: Test mode aggiornato nel DB a: {new_state}")
        
        # Verifica che sia stato salvato correttamente
        verify_state = SystemSettings.get_setting('global_form_test_mode', False)
        print(f"DEBUG: Verifica post-salvataggio: {verify_state}")
        
        action = 'attivata' if new_state else 'disattivata'
        
        return jsonify({
            'message': f'Modalità test globale {action}',
            'test_mode': new_state,
            'changed_by': current_user.username,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Errore nel cambio modalità test: {str(e)}'}), 500


# === EXPORT CANDIDATI PER OSPITI ===

@main.route('/api/candidates/export')
@login_required
@view_only_required('ospite')
def export_candidates():
    """Esporta lista candidati in formato CSV per utenti ospite"""
    import csv
    from io import StringIO
    from flask import make_response
    
    candidates = Candidate.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header CSV
    writer.writerow([
        'Nome', 'Cognome', 'Email', 'Telefono', 'Città', 
        'Genere', 'Stato', 'Data Creazione'
    ])
    
    # Dati candidati
    for candidate in candidates:
        writer.writerow([
            candidate.first_name or '',
            candidate.last_name or '',
            candidate.email or '',
            candidate.phone or '',
            candidate.city or '',
            candidate.gender or '',
            candidate.status or '',
            candidate.created_at.strftime('%d/%m/%Y %H:%M') if candidate.created_at else ''
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=candidati.csv'
    
    return response


# ===============================
# API GESTIONE CONFIGURAZIONE CAMPI FORM DINAMICO
# ===============================

@main.route('/api/form/<int:form_id>/fields-config', methods=['GET'])
@login_required
@role_required('intervistatore')
def get_form_fields_config(form_id):
    """Ottiene la configurazione dei campi per un form specifico"""
    try:
        # Verifica che il form esista
        form = DynamicForm.query.get_or_404(form_id)
        
        # Ottieni la configurazione esistente
        existing_configs = FormFieldConfiguration.get_form_configuration(form_id)
        
        # Ottieni i campi predefiniti
        default_fields = FormFieldConfiguration.get_default_fields()
        
        # Crea la configurazione completa
        fields_config = {}
        for field_name, field_info in default_fields.items():
            config = existing_configs.get(field_name)
            fields_config[field_name] = {
                'label': field_info['label'],
                'step': field_info['step'],
                'section': field_info['section'],
                'is_visible': config.is_visible if config else True,
                'is_required': config.is_required if config else True,
                'field_order': config.field_order if config else 0
            }
        
        return jsonify({
            'success': True,
            'form_id': form_id,
            'form_name': form.name,
            'fields': fields_config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Errore nel caricamento configurazione: {str(e)}'
        }), 500


@main.route('/api/form/<int:form_id>/fields-config', methods=['POST'])
@login_required
@role_required('intervistatore')
def update_form_fields_config(form_id):
    """Aggiorna la configurazione dei campi per un form specifico"""
    try:
        # Verifica che il form esista
        form = DynamicForm.query.get_or_404(form_id)
        
        data = request.get_json()
        if not data or 'fields' not in data:
            return jsonify({
                'success': False,
                'error': 'Dati di configurazione mancanti'
            }), 400
        
        updated_fields = []
        
        # Aggiorna ogni campo
        for field_name, config in data['fields'].items():
            is_visible = config.get('is_visible', True)
            is_required = config.get('is_required', True)
            
            # Salva la configurazione
            field_config = FormFieldConfiguration.set_field_config(
                form_id=form_id,
                field_name=field_name,
                is_visible=is_visible,
                is_required=is_required,
                user_id=current_user.id
            )
            
            updated_fields.append({
                'field_name': field_name,
                'is_visible': is_visible,
                'is_required': is_required
            })
        
        return jsonify({
            'success': True,
            'message': f'Configurazione aggiornata per {len(updated_fields)} campi',
            'updated_fields': updated_fields
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Errore nell\'aggiornamento configurazione: {str(e)}'
        }), 500


@main.route('/gestione-form/<int:form_id>/campi')
@login_required
@role_required('intervistatore')
def manage_form_fields(form_id):
    """Pagina per la gestione dei campi di un form dinamico"""
    form = DynamicForm.query.get_or_404(form_id)
    
    breadcrumbs = [
        {'name': 'Dashboard', 'url': url_for('main.dashboard')},
        {'name': 'Form Dinamici', 'url': url_for('main.list_dynamic_forms')},
        {'name': form.name, 'url': url_for('main.edit_dynamic_form', form_id=form_id)},
        {'name': 'Gestione Campi', 'url': None}
    ]
    
    return render_template('manage_form_fields.html', 
                         form=form, 
                         sidebar=True, 
                         breadcrumbs=breadcrumbs)