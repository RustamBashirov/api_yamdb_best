from datetime import datetime

from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'rating',
                  'description',
                  'genre',
                  'category')


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=False,
        allow_null=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    year = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        if value > datetime.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!')
        return value

    def to_representation(self, title):
        serializer = TitleSerializer(title)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        user = self.context['request'].user
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        validators=[UniqueValidator(queryset=User.objects.all())],
        max_length=150,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        max_length=254,
    )

    class Meta:
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')
        model = User


class UsernameSerializer(serializers.Serializer):
    username = serializers.RegexField(
        required=True, max_length=150, regex=r'^[\w.@+-]+$'
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('me - не допустимое имя')
        return value


class RegisterDataSerializer(UsernameSerializer):
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        fields = ('email', 'username',)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(email=email).exists(
        ) and not User.objects.filter(username=username, email=email).exists():
            raise serializers.ValidationError(
                'Такой пользователь с таким email уже существует')
        if User.objects.filter(username=username).exists(
        ) and not User.objects.filter(username=username, email=email).exists():
            raise serializers.ValidationError(
                'Такой пользователй с таким логином уже существует')
        return data

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data.get('username'),
            defaults={'email': validated_data.get('email')}
        )
        if not created and user.email != validated_data.get('email'):
            raise serializers.ValidationError(
                'Такой пользователь с таким email уже существует')
        return user

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data.get('username'),
            defaults={'email': validated_data.get('email')}
        )
        if not created and user.email != validated_data.get('email'):
            raise serializers.ValidationError(
                'Такой пользователь с таким email уже существует')
        return user


class TokenSerializer(UsernameSerializer):
    confirmation_code = serializers.CharField()

    class Meta:
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения')
        data['user'] = user
        return data
