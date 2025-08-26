"""Utilidades generales del core."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import re
import hashlib
import secrets
import string
from uuid import uuid4


def generate_uuid() -> str:
    """Genera un UUID único."""
    return str(uuid4())


def generate_random_string(length: int = 32) -> str:
    """Genera una cadena aleatoria segura."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{password_hash.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash."""
    try:
        salt, password_hash = hashed.split(':')
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == password_hash
    except ValueError:
        return False


def validate_email(email: str) -> bool:
    """Valida formato de email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_cedula(cedula: str) -> bool:
    """Valida formato de cédula colombiana."""
    if not cedula or not cedula.isdigit():
        return False
    return 6 <= len(cedula) <= 10


def validate_phone(phone: str) -> bool:
    """Valida formato de teléfono."""
    pattern = r'^[+]?[0-9]{7,15}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


def sanitize_string(text: str) -> str:
    """Sanitiza una cadena removiendo caracteres especiales."""
    if not text:
        return ""
    # Remover caracteres especiales pero mantener espacios, letras, números y algunos símbolos básicos
    return re.sub(r'[^\w\s.-]', '', text).strip()


def format_datetime(dt: datetime) -> str:
    """Formatea datetime a string ISO."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def parse_datetime(dt_str: str) -> datetime:
    """Parsea string ISO a datetime."""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


def get_current_datetime() -> datetime:
    """Obtiene la fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


def paginate_results(items: List[Any], page: int, size: int) -> Dict[str, Any]:
    """Pagina una lista de elementos."""
    if page < 1:
        page = 1
    if size < 1:
        size = 10
    
    start_index = (page - 1) * size
    end_index = start_index + size
    
    paginated_items = items[start_index:end_index]
    total_items = len(items)
    total_pages = (total_items + size - 1) // size
    
    return {
        "items": paginated_items,
        "pagination": {
            "page": page,
            "size": size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }


def clean_dict(data: Dict[str, Any], remove_none: bool = True, remove_empty: bool = False) -> Dict[str, Any]:
    """Limpia un diccionario removiendo valores None y/o vacíos."""
    cleaned = {}
    for key, value in data.items():
        if remove_none and value is None:
            continue
        if remove_empty and value == "":
            continue
        if isinstance(value, dict):
            cleaned_value = clean_dict(value, remove_none, remove_empty)
            if cleaned_value:  # Solo agregar si el diccionario no está vacío
                cleaned[key] = cleaned_value
        else:
            cleaned[key] = value
    return cleaned


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Combina múltiples diccionarios."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def extract_numbers(text: str) -> List[int]:
    """Extrae todos los números de una cadena."""
    return [int(match) for match in re.findall(r'\d+', text)]


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Trunca una cadena a una longitud máxima."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def normalize_string(text: str) -> str:
    """Normaliza una cadena (minúsculas, sin espacios extra)."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip().lower())


def is_valid_objectid(object_id: str) -> bool:
    """Valida si una cadena es un ObjectId válido de MongoDB."""
    return bool(re.match(r'^[0-9a-fA-F]{24}$', object_id))


def format_file_size(size_bytes: int) -> str:
    """Formatea el tamaño de archivo en bytes a formato legible."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Obtiene un valor de un diccionario de forma segura."""
    return dictionary.get(key, default)


def convert_to_bool(value: Union[str, bool, int, None]) -> bool:
    """Convierte diferentes tipos de valores a booleano."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    if isinstance(value, int):
        return value != 0
    return False