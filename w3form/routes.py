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

@main.route('/candidato/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('intervistatore')
def edit_candidate(id):
    # TODO: implementare form e logica modifica
    return render_template('candidate_form.html')

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
        'auto_moto_munito', 'proficiency_1', 'proficiency_2', 'proficiency_3'
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
        'auto_moto_munito', 'proficiency_1', 'proficiency_2', 'proficiency_3'
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