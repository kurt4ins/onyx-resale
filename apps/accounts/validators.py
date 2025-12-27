from django.core.exceptions import ValidationError
import re


def normalize_phone(phone):
    cleaned = re.sub(r'[\s\-\(\)]', '', str(phone))
    
    if cleaned.startswith('8'):
        cleaned = '+7' + cleaned[1:]
    elif not cleaned.startswith('+7'):
        cleaned = '+7' + cleaned
    
    return cleaned


def validate_phone(value):
    cleaned = normalize_phone(value)
    
    if len(cleaned) != 12:
        raise ValidationError('Введите корректный номер телефона')
    
    if not cleaned[2:].isdigit():
        raise ValidationError('Телефон должен содержать только цифры')
