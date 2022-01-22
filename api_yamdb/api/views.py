from django.db.models.aggregates import Avg
from api_yamdb.settings import NO_REPLY_EMAIL
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title
from .filterset import TitleFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly, IsModerator,
                          OnlyOwnerCanEdit)
from .serializers import (AdminUsersSerializer, CategorySerializer,
                          CommentsGetSerializer, GenreSerializer,
                          ReviewsGetSerializer, TitleCreateSerializer,
                          TitleViewSerializer, TokenObtainSerializer,
                          UserProfileSerializer, UserSignupSerializer)

User = get_user_model()


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup_view(request):

    def confirmation_code_send(user_email, confirmation_code):

        letter_body = 'Confirmation code: ' + confirmation_code

        send_mail(
            'Подтверждение регистрации на YaMBD',
            letter_body,
            NO_REPLY_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return confirmation_code

    def confirmation_code_generation(user):
        code = PasswordResetTokenGenerator().make_token(user)
        return code

    serializer = UserSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    user, st = User.objects.get_or_create(email=email, username=username)
    if user.confirmation_code is None:
        code = confirmation_code_generation(user)
        user.confirmation_code = code
        user.save()

    confirmation_code_send(email, user.confirmation_code)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def token_obtain_view(request):
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if PasswordResetTokenGenerator().check_token(user, code):
        token = AccessToken().for_user(user)
        print(token)
        context = {'token': str(token)}
        return Response(context, status=status.HTTP_200_OK)
    error_context = {
        'detail': 'Отстутствует обязательное поле или оно не корректно'}
    return Response(error_context, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    lookup_field = None
    serializer_class = UserProfileSerializer

    def get_object(self):
        user = get_object_or_404(User, username=self.request.user)
        return user


class AdminUsersViewSet(ModelViewSet):

    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = AdminUsersSerializer
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ('username',)
    search_fields = ('username',)


class ClassificationViewSet(mixins.CreateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):

    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ('name',)
    search_fields = ('name',)


class CategoryViewSet(ClassificationViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ClassificationViewSet):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering = ('name',)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleViewSerializer
        return TitleCreateSerializer


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewsGetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          OnlyOwnerCanEdit | IsAdmin | IsModerator]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        reviews = title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentsGetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          OnlyOwnerCanEdit | IsAdmin | IsModerator]

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),
                                   title=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),
                                   title=self.kwargs.get('title_id'))
        comments = review.comments.all()
        return comments
