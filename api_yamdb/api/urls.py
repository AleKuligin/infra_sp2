from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter

from .views import (AdminUsersViewSet, CategoryViewSet, CommentViewSet,
                    GenreViewSet, ReviewViewSet, TitleViewSet,
                    UserProfileViewSet, signup_view, token_obtain_view)

router = DefaultRouter()
router.register('users', AdminUsersViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)

urlpatterns = [
    path('v1/auth/signup/', signup_view, name='user_signup'),
    path('v1/auth/token/', token_obtain_view, name='token_obtain'),
    path('v1/users/me/',
         UserProfileViewSet.as_view({'get': 'retrieve', 'patch': 'update'}),
         name='user_profile'),
    path('v1/', include(router.urls)),
]
