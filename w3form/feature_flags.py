"""
Feature Flags Management
Sistema per gestire le funzionalità attivabili/disattivabili dal developer panel
"""

from flask import g
from w3form.models import FeatureFlag

# Lista delle feature flags disponibili nel sistema
AVAILABLE_FEATURES = {
    'form_field_toggle': {
        'name': 'Attivazione/Disattivazione Campi Form',
        'description': 'Permette di attivare o disattivare specifici campi nei form dinamici',
        'default': True
    },
    'bulk_operations': {
        'name': 'Operazioni di Massa',
        'description': 'Permette operazioni bulk su candidati (eliminazione, modifica, esportazione)',
        'default': True
    },
    'advanced_search': {
        'name': 'Ricerca Avanzata',
        'description': 'Abilita filtri avanzati nella ricerca candidati',
        'default': True
    },
    'data_export': {
        'name': 'Esportazione Dati',
        'description': 'Permette l\'esportazione di dati in vari formati (CSV, PDF, Excel)',
        'default': True
    },
    'candidate_scoring': {
        'name': 'Sistema Punteggi Candidati',
        'description': 'Abilita il sistema di valutazione e punteggi per i candidati',
        'default': True
    }
}

def init_default_features():
    """Inizializza le feature flags di default se non esistono"""
    from w3form import db
    
    for key, config in AVAILABLE_FEATURES.items():
        existing = FeatureFlag.query.filter_by(feature_key=key).first()
        if not existing:
            feature = FeatureFlag(
                feature_key=key,
                feature_name=config['name'],
                description=config['description'],
                is_enabled=config['default']
            )
            db.session.add(feature)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Errore nell'inizializzazione delle feature flags: {e}")

def is_feature_enabled(feature_key):
    """
    Controlla se una funzionalità è abilitata
    
    Args:
        feature_key (str): La chiave della funzionalità da controllare
        
    Returns:
        bool: True se la funzionalità è abilitata, False altrimenti
    """
    # Controllo cache nella sessione Flask
    if not hasattr(g, '_feature_cache'):
        g._feature_cache = {}
    
    if feature_key in g._feature_cache:
        return g._feature_cache[feature_key]
    
    # Query al database
    result = FeatureFlag.is_feature_enabled(feature_key)
    g._feature_cache[feature_key] = result
    
    return result

def get_all_features_status():
    """
    Ottieni lo stato di tutte le feature flags
    
    Returns:
        dict: Dizionario con chiave -> stato abilitato/disabilitato
    """
    features = FeatureFlag.get_all_features()
    status = {}
    
    for feature in features:
        status[feature.feature_key] = {
            'enabled': feature.is_enabled,
            'name': feature.feature_name,
            'description': feature.description
        }
    
    # Aggiungi feature non ancora configurate
    for key, config in AVAILABLE_FEATURES.items():
        if key not in status:
            status[key] = {
                'enabled': config['default'],
                'name': config['name'],
                'description': config['description']
            }
    
    return status

def toggle_feature(feature_key):
    """
    Attiva/disattiva una funzionalità
    
    Args:
        feature_key (str): La chiave della funzionalità da togglere
        
    Returns:
        bool: Il nuovo stato della funzionalità
    """
    from w3form import db
    
    feature = FeatureFlag.query.filter_by(feature_key=feature_key).first()
    
    if not feature:
        # Crea la feature se non esiste
        if feature_key in AVAILABLE_FEATURES:
            config = AVAILABLE_FEATURES[feature_key]
            feature = FeatureFlag(
                feature_key=feature_key,
                feature_name=config['name'],
                description=config['description'],
                is_enabled=not config['default']  # Toglia il default
            )
            db.session.add(feature)
        else:
            return False
    else:
        # Toglia lo stato esistente
        feature.is_enabled = not feature.is_enabled
    
    try:
        db.session.commit()
        # Pulisci la cache
        if hasattr(g, '_feature_cache') and feature_key in g._feature_cache:
            del g._feature_cache[feature_key]
        return feature.is_enabled
    except Exception as e:
        db.session.rollback()
        print(f"Errore nel toggle della feature {feature_key}: {e}")
        return False

def feature_required(feature_key):
    """
    Decorator per richiedere che una feature sia abilitata
    
    Usage:
        @feature_required('form_field_toggle')
        def my_view():
            pass
    """
    def decorator(f):
        from functools import wraps
        from flask import abort, jsonify, request
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_feature_enabled(feature_key):
                if request.is_json:
                    return jsonify({
                        'error': 'Funzionalità non disponibile',
                        'feature': feature_key
                    }), 403
                else:
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
