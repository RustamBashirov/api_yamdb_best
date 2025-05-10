from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator, MaxValueValidator, RegexValidator
)

from .validators import validate_year

User = get_user_model()


class Category(models.Model):
    """Модель категорий произведений."""
    name = models.CharField('имя категории', max_length=200)
    slug = models.SlugField(
        'слаг категории',
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=(
                    'Slug может содержать только латинские буквы, '
                    'цифры, дефисы и подчеркивания'
                )
            )
        ],
    )

    class Meta:
        """Класс Meta для настроек модели."""
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        """Строковое представление объекта категории."""
        return self.name


class Genre(models.Model):
    """Модель жанров произведений."""
    name = models.CharField('имя жанра', max_length=200)
    slug = models.SlugField(
        'слаг жанра',
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=(
                    'Slug может содержать только латинские буквы, '
                    'цифры, дефисы и подчеркивания'
                )
            )
        ],
    )

    class Meta:
        """Класс Meta для настроек модели."""
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        """Строковое представление объекта жанра."""
        return self.name


class Title(models.Model):
    """Модель произведений (фильмов, книг, песен и т.д.)."""
    name = models.CharField('название', max_length=200)
    year = models.IntegerField('год', validators=(validate_year,))
    description = models.CharField(
        'описание',
        max_length=255,
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='категория',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='жанр'
    )

    class Meta:
        """Класс Meta для настроек модели."""
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        """Строковое представление объекта произведения."""
        return self.name


class Review(models.Model):
    """Модель отзывов на произведения."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    text = models.TextField(
        'текст отзыва'
    )
    score = models.IntegerField(
        'оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        )
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True
    )

    class Meta:
        """Класс Meta для настроек модели."""
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]
        ordering = ['-pub_date']

    def __str__(self):
        """Строковое представление объекта отзыва."""
        return f'Отзыв на {self.title} от {self.author}'


class Comment(models.Model):
    """Модель комментариев на отзывы."""

    text = models.TextField(verbose_name='текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Aвтор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='oтзыв',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        """Строковое представление объекта комментария."""
        return self.text
