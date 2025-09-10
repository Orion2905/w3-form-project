# Script per aggiungere candidati di test al database
from w3form.models import db, Candidate, Photo, Curriculum, DynamicForm, User
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
        codice_fiscale="RSSMRA90E15F205Z",
        license_country="Italia",
        license_number="MI1234567",
        license_category="B",
        license_issue_date=date(2008, 6, 1),
        license_expiry_date=date(2030, 6, 1),
        years_driving_experience=15,
        auto_moto_munito=True,
        occupation="Sviluppatore Python",
        other_experience="Esperienza in sviluppo web e automazione.",
        availability_from=date(2024, 7, 1),
        availability_till=date(2024, 12, 31),
        city_availability="Milano, Roma",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Avanzato",
        language_3="Francese",
        proficiency_3="Base",
        come_sei_arrivato="Sito web",
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
        codice_fiscale="BNCGLI95M62H501A",
        license_country="Italia",
        license_number="RM9876543",
        license_category="B",
        license_issue_date=date(2013, 9, 1),
        license_expiry_date=date(2029, 9, 1),
        years_driving_experience=12,
        auto_moto_munito=True,
        occupation="Data Analyst",
        other_experience="Stage in azienda di consulenza dati.",
        availability_from=date(2024, 8, 1),
        availability_till=date(2025, 1, 31),
        city_availability="Roma, Napoli",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Intermedio",
        language_3="Spagnolo",
        proficiency_3="Base",
        come_sei_arrivato="LinkedIn",
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
        codice_fiscale="VRDLCU85B10L219H",
        license_country="Italia",
        license_number="TO9988776",
        license_category="B",
        license_issue_date=date(2003, 3, 1),
        license_expiry_date=date(2028, 3, 1),
        years_driving_experience=21,
        auto_moto_munito=True,
        occupation="Project Manager",
        other_experience="Gestione team e progetti IT.",
        availability_from=date(2024, 9, 1),
        availability_till=date(2025, 2, 28),
        city_availability="Torino, Milano",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Avanzato",
        language_3="Tedesco",
        proficiency_3="Base",
        come_sei_arrivato="Passaparola",
        created_at=datetime(2024, 6, 3)
    ),
    # Candidato con disponibilità passata (per testare i filtri)
    Candidate(
        first_name="Anna",
        last_name="Ferrari",
        gender="F",
        date_of_birth=date(1992, 11, 5),
        place_of_birth="Firenze",
        nationality="Italiana",
        marital_status="Sposata",
        height_cm=170,
        weight_kg=62,
        tshirt_size="M",
        shoe_size_eu="39",
        phone_number="3334445566",
        email="anna.ferrari@example.com",
        address="Via dei Medici 15",
        city="Firenze",
        postal_code="50100",
        country_of_residence="Italia",
        id_document="Carta identità",
        id_number="FI4445566",
        id_expiry_date=date(2031, 11, 5),
        id_country="Italia",
        codice_fiscale="FRRANN92S45D612F",
        license_country="Italia",
        license_number="FI1122334",
        license_category="B",
        license_issue_date=date(2010, 12, 1),
        license_expiry_date=date(2031, 12, 1),
        years_driving_experience=14,
        auto_moto_munito=False,
        occupation="Marketing Manager",
        other_experience="Esperienza in campagne digital e social media.",
        availability_from=date(2024, 1, 1),
        availability_till=date(2024, 3, 31),  # Disponibilità passata
        city_availability="Firenze, Bologna",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Avanzato",
        language_3="Francese",
        proficiency_3="Intermedio",
        come_sei_arrivato="Google",
        created_at=datetime(2024, 5, 15)
    ),
    # Candidato disponibile ora (per testare filtro "available-now")
    Candidate(
        first_name="Marco",
        last_name="Conti",
        gender="M",
        date_of_birth=date(1988, 3, 12),
        place_of_birth="Bologna",
        nationality="Italiana",
        marital_status="Celibe",
        height_cm=185,
        weight_kg=78,
        tshirt_size="L",
        shoe_size_eu="45",
        phone_number="3337778899",
        email="marco.conti@example.com",
        address="Via Indipendenza 22",
        city="Bologna",
        postal_code="40100",
        country_of_residence="Italia",
        id_document="Passaporto",
        id_number="AA7778899",
        id_expiry_date=date(2032, 3, 12),
        id_country="Italia",
        codice_fiscale="CNTMRC88C12A944G",
        license_country="Italia",
        license_number="BO7778899",
        license_category="B+E",
        license_issue_date=date(2006, 4, 1),
        license_expiry_date=date(2032, 4, 1),
        years_driving_experience=18,
        auto_moto_munito=True,
        occupation="Ingegnere Informatico",
        other_experience="Sviluppo software e gestione infrastrutture cloud.",
        availability_from=date(2024, 6, 1),
        availability_till=date(2025, 12, 31),  # Disponibile ora
        city_availability="Bologna, Milano, Roma",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Avanzato",
        language_3="Tedesco",
        proficiency_3="Intermedio",
        come_sei_arrivato="Agenzia di lavoro",
        created_at=datetime(2024, 7, 10)  # Candidato recente
    ),
    # Candidato con poca esperienza di guida (per testare filtro esperti)
    Candidate(
        first_name="Sofia",
        last_name="Lombardi",
        gender="F",
        date_of_birth=date(2000, 7, 18),
        place_of_birth="Venezia",
        nationality="Italiana",
        marital_status="Nubile",
        height_cm=162,
        weight_kg=55,
        tshirt_size="S",
        shoe_size_eu="37",
        phone_number="3332223344",
        email="sofia.lombardi@example.com",
        address="Castello 1234",
        city="Venezia",
        postal_code="30100",
        country_of_residence="Italia",
        id_document="Carta identità",
        id_number="VE2223344",
        id_expiry_date=date(2030, 7, 18),
        id_country="Italia",
        codice_fiscale="LMBSFO00L58L736B",
        license_country="Italia",
        license_number="VE5566778",
        license_category="B",
        license_issue_date=date(2018, 8, 1),
        license_expiry_date=date(2030, 8, 1),
        years_driving_experience=3,  # Poca esperienza
        auto_moto_munito=False,
        occupation="Studentessa Universitaria",
        other_experience="Stage in azienda di turismo.",
        availability_from=date(2024, 9, 1),
        availability_till=date(2024, 12, 31),
        city_availability="Venezia, Padova",
        language_1="Italiano",
        proficiency_1="Madrelingua",
        language_2="Inglese",
        proficiency_2="Intermedio",
        language_3="Spagnolo",
        proficiency_3="Base",
        come_sei_arrivato="Social media",
        created_at=datetime(2024, 7, 20)  # Candidato molto recente
    ),
]

def add_candidates():
    with app.app_context():
        added_count = 0
        for c in test_candidates:
            exists = Candidate.query.filter_by(email=c.email).first()
            if not exists:
                db.session.add(c)
                db.session.flush()  # Ottieni l'id del candidato
                
                # Aggiungi foto profilo placeholder
                photo = Photo(candidate_id=c.id, filename="static/testfiles/placeholder_profile.jpg")
                db.session.add(photo)
                
                # Aggiungi curriculum placeholder
                cv = Curriculum(candidate_id=c.id, filename="static/testfiles/placeholder_cv.pdf")
                db.session.add(cv)
                
                added_count += 1
                print(f"✓ Aggiunto candidato: {c.first_name} {c.last_name}")
            else:
                print(f"- Candidato già esistente: {c.first_name} {c.last_name}")
        
        db.session.commit()
        print(f"\n📊 Risultato: {added_count}/{len(test_candidates)} candidati aggiunti al database.")
        if added_count > 0:
            print("🔗 Foto e CV placeholder associati ai nuovi candidati.")

def add_test_scores():
    """Aggiunge punteggi di test per alcuni candidati"""
    from w3form.models import Score, User
    
    with app.app_context():
        # Verifica se esiste un utente admin per assegnare i punteggi
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("⚠️  Nessun utente 'admin' trovato. I punteggi saranno aggiunti senza evaluator.")
            admin_user = None
        
        # Ottieni alcuni candidati per aggiungere punteggi di test
        mario = Candidate.query.filter_by(email="mario.rossi@example.com").first()
        giulia = Candidate.query.filter_by(email="giulia.bianchi@example.com").first()
        marco = Candidate.query.filter_by(email="marco.conti@example.com").first()
        
        test_scores = []
        
        if mario:
            test_scores.extend([
                Score(candidate_id=mario.id, user_id=admin_user.id if admin_user else None,
                      category="Intervista Tecnica", score=85, max_score=100, weight=3.0,
                      notes="Ottime competenze tecniche, esperienza solida."),
                Score(candidate_id=mario.id, user_id=admin_user.id if admin_user else None,
                      category="Soft Skills", score=75, max_score=100, weight=2.0,
                      notes="Buone capacità comunicative, lavoro di squadra."),
                Score(candidate_id=mario.id, user_id=admin_user.id if admin_user else None,
                      category="Esperienza", score=90, max_score=100, weight=2.5,
                      notes="Lunga esperienza nel settore."),
            ])
        
        if giulia:
            test_scores.extend([
                Score(candidate_id=giulia.id, user_id=admin_user.id if admin_user else None,
                      category="Analisi Dati", score=95, max_score=100, weight=3.0,
                      notes="Eccellenti competenze analitiche."),
                Score(candidate_id=giulia.id, user_id=admin_user.id if admin_user else None,
                      category="Soft Skills", score=88, max_score=100, weight=2.0,
                      notes="Ottime capacità di presentazione."),
            ])
        
        if marco:
            test_scores.extend([
                Score(candidate_id=marco.id, user_id=admin_user.id if admin_user else None,
                      category="Competenze Tecniche", score=92, max_score=100, weight=3.0,
                      notes="Eccellenti competenze in cloud computing."),
                Score(candidate_id=marco.id, user_id=admin_user.id if admin_user else None,
                      category="Leadership", score=70, max_score=100, weight=1.5,
                      notes="Buone basi, da sviluppare."),
                Score(candidate_id=marco.id, user_id=admin_user.id if admin_user else None,
                      category="Problem Solving", score=87, max_score=100, weight=2.0,
                      notes="Approccio metodico e efficace."),
            ])
        
        added_scores = 0
        for score in test_scores:
            # Verifica se il punteggio esiste già
            existing = Score.query.filter_by(
                candidate_id=score.candidate_id, 
                category=score.category
            ).first()
            if not existing:
                db.session.add(score)
                added_scores += 1
        
        db.session.commit()
        print(f"📈 Aggiunti {added_scores} punteggi di test.")

def add_test_forms():
    """Aggiunge form di test se non esistono"""
    with app.app_context():
        test_forms = [
            DynamicForm(
                name="Candidatura Evento Aziendale",
                slug="evento-aziendale",
                description="Form per candidati interessati a eventi aziendali",
                category="Evento",
                subcategory="Aziendale",
                dropdown_options={
                    'come_sei_arrivato': ['Sito web', 'LinkedIn', 'Google', 'Passaparola', 'Social media', 'Agenzia di lavoro'],
                    'gender': ['M', 'F', 'Altro'],
                    'marital_status': ['Celibe', 'Nubile', 'Sposato/a', 'Divorziato/a', 'Vedovo/a']
                }
            ),
            DynamicForm(
                name="Candidatura Hostess/Steward",
                slug="hostess-steward",
                description="Form per candidati hostess e steward",
                category="Lavoro",
                subcategory="Hospitality",
                dropdown_options={
                    'come_sei_arrivato': ['Sito web', 'LinkedIn', 'Google', 'Passaparola', 'Social media', 'Agenzia di lavoro'],
                    'gender': ['M', 'F', 'Altro'],
                    'marital_status': ['Celibe', 'Nubile', 'Sposato/a', 'Divorziato/a', 'Vedovo/a']
                }
            )
        ]
        
        added_forms = 0
        for form in test_forms:
            existing = DynamicForm.query.filter_by(slug=form.slug).first()
            if not existing:
                db.session.add(form)
                added_forms += 1
                print(f"✓ Aggiunto form: {form.name}")
            else:
                print(f"- Form già esistente: {form.name}")
        
        db.session.commit()
        print(f"📋 Aggiunti {added_forms} form di test.")
        return added_forms

def add_test_user():
    """Aggiunge un utente admin di test se non esiste"""
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('admin123')  # Password di test
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Aggiunto utente admin di test (username: admin, password: admin123)")
            return True
        else:
            print("- Utente admin già esistente")
            return False

if __name__ == "__main__":
    print("🚀 Avvio configurazione database di test...")
    
    print("\n1️⃣ Aggiunta form di test...")
    add_test_forms()
    
    print("\n2️⃣ Aggiunta utente admin...")
    add_test_user()
    
    print("\n3️⃣ Aggiunta candidati di test...")
    add_candidates()
    
    print("\n📊 Vuoi aggiungere anche punteggi di test? (y/n)")
    response = input().lower().strip()
    if response in ['y', 'yes', 's', 'si', 'sì']:
        add_test_scores()
    
    print("\n✅ Configurazione database di test completata!")
    print("\n📋 Dati di test disponibili:")
    print("   • 6 candidati con dati completi")
    print("   • 2 form dinamici di esempio")
    print("   • 1 utente admin (admin/admin123)")
    print("   • Punteggi di esempio (se selezionati)")
    print("\n🔍 Puoi ora testare:")
    print("   • Filtri per data (candidati recenti/vecchi)")
    print("   • Filtri per disponibilità (passata/attuale/futura)")
    print("   • Filtri per esperienza di guida (3-21 anni)")
    print("   • Export CSV/PDF con candidati filtrati")
    print("   • Sistema di punteggi (se aggiunti)")
