from django.urls import path

from .views import (
    ProfileDetailView,
    ProfileUpdateView,
    ServiceUserListView,
    UserActivateView,
    UserBlockToggleView,
    UserLoginView,
    UserLogoutView,
    UserPasswordResetCompleteView,
    UserPasswordResetConfirmView,
    UserPasswordResetDoneView,
    UserPasswordResetView,
    UserRegisterView,
)

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', UserActivateView.as_view(), name='activate'),
    path('profile/', ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('manage/', ServiceUserListView.as_view(), name='manage'),
    path('manage/<int:pk>/toggle/', UserBlockToggleView.as_view(), name='manage_toggle'),
]

