from django.urls import path
from .views import (AccountDeleteConfirmAPIView, 
                    AccountDeleteRequestAPIView, 
                    ForgotPasswordAPIView, 
                    PasswordResetConfirmAPIView, 
                    RegisterView, 
                    LoginView, 
                    CheckUsernameView,
                    ProfileUpdateAPIView,
                    PasswordChangeAPIView
                    )


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('profile/',ProfileUpdateAPIView.as_view(),name='profile'),
    path('profile/change-password/',PasswordChangeAPIView.as_view(),name='profile-change-password'),
    path('account/password-reset/', ForgotPasswordAPIView.as_view(), name='password-reset'),
    path('account/password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    path('account/account-delete-request/', AccountDeleteRequestAPIView.as_view(), name='account-delete-request'),
    path('account/account-delete-confirm/<uidb64>/<token>/', AccountDeleteConfirmAPIView.as_view(), name='account-delete-confirm'),
]
