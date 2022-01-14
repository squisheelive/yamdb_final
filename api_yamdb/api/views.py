from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .pagination import UserPagination
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsOwnerAdminModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          CreateAndGetCode, GenreSerializer,
                          GetTokenSerializer, MeSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer)
from api_yamdb.settings import ADMIN_EMAIL
from reviews.models import Category, Genre, Review, Title, User

confirmation_token = PasswordResetTokenGenerator()


@api_view(['POST'])
def create_and_get_code(request):
    serializer = CreateAndGetCode(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    obj, created = User.objects.get_or_create(username=username, email=email)
    if created is False:
        return Response(
            'Такой пользователь уже существует',
            status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = confirmation_token.make_token(user=obj)
    message = f'Ваш код {confirmation_code}'
    send_mail(
        subject='Код подтверждения для YAMDB',
        message=message,
        from_email=ADMIN_EMAIL,
        recipient_list=[email]
    )
    return Response(
        {'email': f'{email}', 'username': f'{username}'},
        status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    code = serializer.validated_data.get('confirmation_code')
    if not User.objects.filter(username=username).exists():
        return Response(
            'Пользователь не найден',
            status=status.HTTP_404_NOT_FOUND)
    user = get_object_or_404(User, username=username)
    if confirmation_token.check_token(user, code):
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response(
        'Отсутствует обязательное поле или оно некорректно',
        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()


class APIMe(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = MeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            'Необходима авторизация',
            status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = MeSerializer(user, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            'Необходима авторизация',
            status=status.HTTP_401_UNAUTHORIZED)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        author = self.request.user
        if Review.objects.filter(author=author, title=title):
            raise serializers.ValidationError(
                'Нельзя добавить больше одной рецензии на произведение!')
        serializer.save(author=author,
                        title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title_id=title_id)
        return review.comment.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title_id=title_id)
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = UserPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = UserPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleFilter(FilterSet):
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'name', 'year']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('review__score')).all()
    serializer_class = TitleWriteSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = UserPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleReadSerializer
        return TitleWriteSerializer
