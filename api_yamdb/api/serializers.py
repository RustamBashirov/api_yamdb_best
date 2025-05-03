from rest_framework import serializers
from django.db import IntegrityError

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class RegisterDataSerializer(serializers.Serializer):
    """Сериализатор для самостоятельной регистрации пользователя."""
    username = serializers.RegexField(
        required=True, max_length=150, regex=r'^(?!me$)[\w]+$'
    )
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        fields = ('username', 'email')

    def create(self, validated_data):
        try:
            user, _ = User.objects.get_or_create(
                username=validated_data['username'],
                email=validated_data['email'],
                defaults={
                    'confirmation_code': validated_data['confirmation_code']
                }
            )
        except IntegrityError:
            raise serializers.ValidationError(
                'Неправильно введен email или username'
            )
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.RegexField(
        required=True, max_length=150, regex=r'^(?!me$)[\w]+$'
    )
    confirmation_code = serializers.CharField()

    class Meta:
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')


class MeSerializer(UserSerializer):
    """Сериализатор для пользователя модели User,
    чтобы он мог просматривать или изменить свой профиль."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title(чтения)."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'rating',
                  'description',
                  'category',
                  'genre')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title(запись)."""
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
