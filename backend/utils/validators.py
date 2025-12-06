# utils/validators.py
import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    
    return None

def validate_username(username):
    """Validate username"""
    if len(username) < 3 or len(username) > 30:
        return "Username must be between 3 and 30 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return "Username can only contain letters, numbers, and underscores"
    
    return None

def validate_date(date_string, format='%Y-%m-%d'):
    """Validate date string"""
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def sanitize_input(text, max_length=None):
    """Sanitize input text"""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    text = text.strip()
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'[\\/*?:"<>|]', '', text)  # Remove file system unsafe chars
    
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def validate_pagination_params(limit, offset):
    """Validate pagination parameters"""
    if limit < 1 or limit > 100:
        return False, "Limit must be between 1 and 100"
    
    if offset < 0:
        return False, "Offset must be non-negative"
    
    return True, None