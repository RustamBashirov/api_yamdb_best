from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .validators import validate_year
from users.models import User


class Category(models.Model):
    """Модель категорий произведений."""
    name = models.CharField(
        'имя категории',
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        'слаг категории',
        unique=True,
        db_index=True
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
    name = models.CharField(
        'имя жанра',
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        'слаг жанра',
        unique=True,
        db_index=True
    )

    class Meta:
        """Класс Meta для настроек модели."""
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        """Строковое представление объекта жанра."""
        return self.name


class Title(models.Model):
    """Модель произведений (фильмов, книг, песен и т.д.)."""
    name = models.CharField(
        'название',
        max_length=200,
        db_index=True,
    )
    year = models.IntegerField(
        'год',
        validators=(validate_year, )
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
        blank=True
    )
    description = models.CharField(
        verbose_name='Описание',
        max_length=255,
        null=True,
        blank=True
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

    def __str__(self):
        """Строковое представление объекта произведения."""
        return self.name


class Review(models.Model):
    """Модель отзывов на произведения."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Aвтор'
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
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        """Класс Meta для настроек модели."""
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв на {self.title} от {self.author}'


class Comment(models.Model):
    """Класс комментариев."""

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

    def __str__(self):
        return self.text
