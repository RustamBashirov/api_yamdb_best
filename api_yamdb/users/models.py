from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """Модель пользователя."""

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLE_CHOICES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )

    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        help_text='Выберите роль пользователя.',
    )
    bio = models.TextField(
        'О себе',
        blank=True,
        help_text='Напишите немного о себе.',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('role',)
        constraints = [
            models.UniqueConstraint(fields=['username'],
                                    name='unique_username'),
            models.UniqueConstraint(fields=['email'],
                                    name='unique_email'),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def validate_username(value):
        if value.lower() == 'me':
            raise ValidationError("Username 'me' is not allowed.")
