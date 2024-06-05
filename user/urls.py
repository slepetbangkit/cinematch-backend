from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
        MyTokenObtainPairView,
        RegisterView,
        UserFollowingView,
        ProfileView,
        searchProfile,
        getActivities
)


urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),

    path('activities/', getActivities, name='activities'),

    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/search', searchProfile, name='search_profiles'),
    path('profile/<str:username>/following/', UserFollowingView.as_view(), name='following'),
]
