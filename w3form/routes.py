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
    User, Candidate
)
from w3form.decorators import role_required
import requests, time
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os



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