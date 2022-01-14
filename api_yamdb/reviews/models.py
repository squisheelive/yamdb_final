from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import MaxYearValidator

CHOICES = (
    ('user', 'user'),
    ('moderator', 'moderator'),
    ('admin', 'admin'),
)


class User(AbstractUser):
    admin = 'admin'
    moderator = 'moderator'
    user = 'user'
    CHOICES = (
        (admin, 'admin'),
        (moderator, 'moderator'),
        (user, 'user'),
    )

    username = models.CharField(
        unique=True,
        max_length=150)
    email = models.EmailField(
        unique=True,
        max_length=254)
    bio = models.CharField(
        'Биография',
        blank=True,
        max_length=300,
    )
    role = models.TextField(choices=CHOICES, default=user)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='uniq_signup'),
        )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name[:20]


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Жанр')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name[:20]


class Title(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='category_title'
    )
    name = models.CharField(max_length=256, verbose_name='Произведение')
    year = models.IntegerField(
        validators=[
            MinValueValidator(1200),
            MaxYearValidator()
        ]
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='genre_title'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return self.name[:20]


class Review(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='review')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='review')
    text = models.TextField()
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'),
        ]
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'
        ordering = ['pub_date']


class Comment(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comment')
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comment')
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарии'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']
