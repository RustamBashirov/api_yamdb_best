from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Валидатор для проверки корректности года."""
    if value > timezone.now().year:
        raise ValidationError(
            'Год должен быть больше 0 и не превышать текущий год'
        )
