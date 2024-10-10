from django.urls import path
from .views import (RegisterView, 
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
    path('profile/change-password/',PasswordChangeAPIView.as_view(),name='profile-change-password')
]
