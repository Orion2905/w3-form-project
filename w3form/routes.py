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
    send_file
)
from flask_login import login_user, login_required, logout_user, current_user
from w3form import db
from w3form.models import (
    User, Candidate, DynamicForm
)
from w3form.decorators import role_required
import requests, time
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from flask import abort
from io import BytesIO
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
    if current_user.role == 'ospite':
        return redirect(url_for('main.add_candidate'))
    candidates = Candidate.query.all()
    return render_template('dashboard.html', candidates=candidates, sidebar=True)

@main.route('/candidato/aggiungi', methods=['GET', 'POST'])
def add_candidate():
    # TODO: implementare form e logica inserimento
    return render_template('candidate_form.html')

@main.route('/candidati')
@login_required
@role_required('intervistatore')
def candidates_list():
    candidates = Candidate.query.all()
    return render_template('candidates_list.html', candidates=candidates)

@main.route('/candidati/modifica/<int:candidate_id>', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def edit_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    if request.method == 'POST':
        candidate.first_name = request.form['first_name']
        candidate.last_name = request.form['last_name']
        candidate.email = request.form['email']
        candidate.phone_number = request.form['phone_number']
        candidate.come_sei_arrivato = request.form['come_sei_arrivato']
        db.session.commit()
        flash('Candidato aggiornato con successo!', 'success')
        return redirect(url_for('main.candidates_list'))
    return render_template('edit_candidate.html', candidate=candidate)

@main.route('/esporta/pdf')
@login_required
@role_required('intervistatore')
def export_pdf():
    # TODO: implementare esportazione PDF
    return 'Funzione esportazione PDF in sviluppo'

@main.route('/esporta/excel')
@login_required
@role_required('intervistatore')
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
        is_active = bool(request.form.get('is_active'))
        active_from = request.form.get('active_from')
        active_until = request.form.get('active_until')
        dropdown_options = {}
        for field in dropdown_fields:
            key = f'opt_{field}'
            val = request.form.get(key, '').strip()
            if val:
                dropdown_options[field] = [v.strip() for v in val.splitlines() if v.strip()]
        form = DynamicForm(
            name=name,
            slug=slug,
            description=description,
            dropdown_options=dropdown_options,
            is_active=is_active,
            active_from=datetime.strptime(active_from, '%Y-%m-%dT%H:%M') if active_from else None,
            active_until=datetime.strptime(active_until, '%Y-%m-%dT%H:%M') if active_until else None
        )
        db.session.add(form)
        db.session.commit()
        flash('Form creato! Link: ' + url_for('main.public_dynamic_form', slug=slug, _external=True), 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('dynamic_form_create.html', dropdown_fields=dropdown_fields)

@main.route('/forms')
def list_dynamic_forms():
    forms = DynamicForm.query.all()
    return render_template('dynamic_form_list.html', forms=forms)

@main.route('/form/<slug>', methods=['GET'])
def public_dynamic_form(slug):
    form = DynamicForm.query.filter_by(slug=slug).first_or_404()
    now = datetime.utcnow()
    if not form.is_active or (form.active_from and now < form.active_from) or (form.active_until and now > form.active_until):
        return render_template('404.html'), 404
    dropdown_options = form.dropdown_options or {}
    return render_template('dynamic_form_public.html', form=form, dropdown_options=dropdown_options)

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
        db.session.commit()
        flash('Form aggiornato con successo!', 'success')
        return redirect(url_for('main.list_dynamic_forms'))
    # Per la GET, mostra il form di modifica con i dati precompilati
    return render_template('dynamic_form_create.html', form=form, dropdown_fields=dropdown_fields, dropdown_options=form.dropdown_options or {})

@main.route('/api/candidates', methods=['GET'])
@login_required
@role_required('intervistatore')
def api_get_candidates():
    candidates = Candidate.query.all()
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
            'availability': c.availability,
            'other_location': c.other_location,
            'language_1': c.language_1,
            'proficiency_1': c.proficiency_1,
            'language_2': c.language_2,
            'proficiency_2': c.proficiency_2,
            'language_3': c.language_3,
            'proficiency_3': c.proficiency_3,
            'curriculum_file': url_for('main.serve_curriculum', filename=c.curricula[0].filename) if c.curricula else '',
            'profile_photo': url_for('main.serve_photo', filename=c.photos[0].filename) if c.photos else ''
        } for c in candidates
    ])

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
    c.availability = data.get('availability', c.availability)
    c.other_location = data.get('other_location', c.other_location)
    c.language_1 = data.get('language_1', c.language_1)
    c.proficiency_1 = data.get('proficiency_1', c.proficiency_1)
    c.language_2 = data.get('language_2', c.language_2)
    c.proficiency_2 = data.get('proficiency_2', c.proficiency_2)
    c.language_3 = data.get('language_3', c.language_3)
    c.proficiency_3 = data.get('proficiency_3', c.proficiency_3)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/file/curriculum/<filename>')
@login_required
@role_required('intervistatore')
def serve_curriculum(filename):
    AZURE_CONNECTION_STRING = os.environ.get('AZURE_CONNECTION_STRING') or current_app.config.get('AZURE_CONNECTION_STRING')
    if not AZURE_CONNECTION_STRING:
        return 'Azure connection string non configurata', 500
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container='candidati-files', blob=filename)
        stream = BytesIO()
        blob_data = blob_client.download_blob()
        blob_data.readinto(stream)
        stream.seek(0)
        return send_file(stream, download_name=filename, as_attachment=False)
    except Exception as e:
        return f'Errore accesso file: {str(e)}', 500

@main.route('/file/photo/<filename>')
@login_required
@role_required('intervistatore')
def serve_photo(filename):
    AZURE_CONNECTION_STRING = os.environ.get('AZURE_CONNECTION_STRING') or current_app.config.get('AZURE_CONNECTION_STRING')
    if not AZURE_CONNECTION_STRING:
        return 'Azure connection string non configurata', 500
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container='candidati-files', blob=filename)
        stream = BytesIO()
        blob_data = blob_client.download_blob()
        blob_data.readinto(stream)
        stream.seek(0)
        return send_file(stream, download_name=filename, as_attachment=False)
    except Exception as e:
        return f'Errore accesso file: {str(e)}', 500

@main.route('/success')
def success():
    return render_template('success.html')