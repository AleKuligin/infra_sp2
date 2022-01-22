from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, allow_blank=False)
    username = serializers.CharField(max_length=150, allow_blank=False,
                                     validators=[UnicodeUsernameValidator])

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Данное имя пользователя недопустимо!'
            )
        return value

    def validate(self, attrs):
        super().validate(attrs)
        user = attrs['username']
        email = attrs['email']
        if User.objects.filter(email=email, username=user).exists():
            return attrs
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Email уже используется'
            )
        if User.objects.filter(username=user).exists():
            raise serializers.ValidationError(
                'Username уже используется'
            )
        return attrs


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=200, required=True)


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')
        extra_kwargs = {'username': {'required': False}}

    def validate_role(self, value):
        user = self.context['request'].user
        if not user.is_admin:
            if not user.is_superuser:
                value = user.role
        return value


class AdminUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        user = self.context['request'].data.get('username')
        if User.objects.filter(email=value).exclude(username=user).exists():
            raise serializers.ValidationError(
                'Поле e-mail должно быть уникальным!'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')

    def create(self, validated_data):
        category = Category.objects.create(**validated_data)
        return category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')

    def create(self, validated_data):
        genre = Genre.objects.create(**validated_data)
        return genre


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(many=True, write_only=True,
                                         slug_field='slug', required=False,
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(many=False, write_only=True,
                                            slug_field='slug', required=False,
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        if not 0 < value < date.today().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли!'
            )
        return value


class TitleViewSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, required=False)
    genre = GenreSerializer(many=True, required=False)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')
        read_only_fields = ('genre', 'category', 'rating')


class ReviewsGetSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']

        if request.method != 'POST':
            return data

        user = request.user
        title_id = (
            request.parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=user, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение'
            )
        return data


class CommentsGetSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
