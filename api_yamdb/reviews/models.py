from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

USER_ROLES = (
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    role = models.CharField(
        max_length=50,
        choices=USER_ROLES,
        default=USER
    )
    bio = models.CharField(max_length=1000, blank=True, null=True)
    email = models.EmailField(_('email address'), blank=True, null=False,
                              max_length=254)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    confirmation_code = models.CharField(max_length=200, blank=True, null=True)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN


class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=150)
    year = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(date.today().year)])
    category = models.ForeignKey(
        Category, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='titles'
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    description = models.CharField(max_length=2000, blank=True, null=True,
                                   default='')

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, blank=False, null=False,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.CharField(max_length=2000)
    author = models.ForeignKey(
        User, blank=False, null=False,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)])
    pub_date = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='one_review_by_an_author_for_a_title'
            )
        ]
        ordering = ['pub_date']


class Comment(models.Model):
    review = models.ForeignKey(
        Review, blank=False, null=False,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.CharField(max_length=2000)
    author = models.ForeignKey(
        User, blank=False, null=False,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-pub_date']


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_genre_for_a_title'
            )
        ]
