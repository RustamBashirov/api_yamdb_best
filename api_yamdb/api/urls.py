from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       RegisterView, ReviewViewSet, TitleViewSet, TokenView,
                       UserViewSet)


router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

auth_patterns = [
    path('signup/', RegisterView.as_view()),
    path('token/', TokenView.as_view()),
]

urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/', include((router_v1.urls))),
]
