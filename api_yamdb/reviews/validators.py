from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Валидатор для проверки корректности года."""
    current_year = timezone.now().year
    if not (0 <= value <= current_year):
        raise ValidationError(
            'Год должен быть больше 0 и не превышать текущий год'
        )