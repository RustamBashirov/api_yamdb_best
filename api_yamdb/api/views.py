import uuid

from rest_framework import views, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.db.models import Avg

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .mixins import (ListCreateDestroyMixin,
                     RetrieveListCreatePartialUpdateDestroyMixin)
from .premissions import (IsAdmin,
                          ReadOnly,
                          IsAuthorOrAdminOrModeratorOrReadOnly)
from .serializers import (
    CategorySerializer, CommentSerializer,
    GenreSerializer, RegisterDataSerializer,
    ReviewSerializer, TitleSerializer, TitleWriteSerializer,
    TokenSerializer, UserSerializer, MeSerializer
)


class RegisterView(views.APIView):

    def post(self, request):
        serializer = RegisterDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = str(uuid.uuid4())
        serializer.save(confirmation_code=confirmation_code)
        send_mail(
            subject='Регистрация',
            message=f'Код подтверждения регистрации: {confirmation_code}',
            from_email=None,
            recipient_list=[serializer.validated_data['email']],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if confirmation_code == user.confirmation_code:
            token = RefreshToken.for_user(user)
            return Response({'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(RetrieveListCreatePartialUpdateDestroyMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
    )
    def user_me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = MeSerializer(user)
        else:
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnly | IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [ReadOnly | IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(RetrieveListCreatePartialUpdateDestroyMixin):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-rating')
    permission_classes = [ReadOnly | IsAdmin]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleWriteSerializer


class ReviewViewSet(RetrieveListCreatePartialUpdateDestroyMixin):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        author = self.request.user
        if Review.objects.filter(author=author, title=title).exists():
            raise ValidationError(
                'Вы уже оставляли отзыв на это произведение.')
        serializer.save(author=author, title=title)


class CommentViewSet(RetrieveListCreatePartialUpdateDestroyMixin):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly]

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
