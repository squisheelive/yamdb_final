from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, basename='userviewset')
router.register(
    r'titles/(?P<title_id>[^/.]+)/reviews',
    views.ReviewViewSet,
    basename='reviews')
router.register(
    r'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    views.CommentViewSet,
    basename='comments')
router.register(r'categories', views.CategoryViewSet, basename='categories')
router.register(r'genres', views.GenreViewSet, basename='genres')
router.register(r'titles', views.TitleViewSet, basename='titles')

urlpatterns = [
    path(
        'v1/auth/signup/',
        views.create_and_get_code,
        name='create_and_get_code'),
    path('v1/auth/token/', views.get_token, name='get_token'),
    path('v1/users/me/', views.APIMe.as_view(), name='apime'),
    path('v1/', include(router.urls)),
]
