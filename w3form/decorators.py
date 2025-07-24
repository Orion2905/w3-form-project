from flask_login import current_user
from functools import wraps
from flask import abort

def role_required(*roles):
    """
    Decorator per richiedere uno specifico ruolo o set di ruoli.
    Gli utenti developer hanno accesso automatico a tutto.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            
            # Gli utenti developer hanno accesso a tutto
            if current_user.role == 'developer':
                return f(*args, **kwargs)
            
            # Per altri ruoli, controlla se il ruolo è in quelli consentiti
            if current_user.role not in roles:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def developer_required(f):
    """Decorator per funzioni accessibili solo ai developer"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'developer':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def view_only_required(*roles):
    """
    Decorator per funzioni di sola visualizzazione.
    Gli ospiti possono accedere a queste funzioni insieme ai ruoli specificati.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            
            # Gli utenti developer hanno accesso a tutto
            if current_user.role == 'developer':
                return f(*args, **kwargs)
            
            # Gli ospiti hanno accesso alle funzioni di sola visualizzazione
            if current_user.role == 'ospite':
                return f(*args, **kwargs)
            
            # Per altri ruoli, controlla se il ruolo è in quelli consentiti
            if current_user.role not in roles:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator