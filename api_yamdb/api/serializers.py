import datetime

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=256)
    year = serializers.IntegerField(required=True)
    genre = serializers.SlugRelatedField(
        required=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        required=True,
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('__all__')

    def validate_year(self, value):
        current_year = datetime.datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Это из будущего!')
        return value


class TitleReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=256)
    year = serializers.IntegerField(required=True)
    genre = GenreSerializer(many=True, required=True)
    category = CategorySerializer(required=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('__all__')

    def get_rating(self, obj):
        return obj.rating


class CreateAndGetCode(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        min_length=3,
        allow_blank=False)
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=254)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError('Такой пользователь уже существует')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return value


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=254)
    username = serializers.CharField(
        required=True,
        max_length=150,
        min_length=3,
        allow_blank=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Такой пользователь уже существует')
        if username == 'me':
            raise ValidationError('Данный юзернейм недоступен')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return data


class MeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role')
        read_only_fields = ('role',)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        min_length=3,
        allow_blank=False)
    confirmation_code = serializers.CharField(
        required=True,
        min_length=5,
        allow_blank=False)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='name')

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
