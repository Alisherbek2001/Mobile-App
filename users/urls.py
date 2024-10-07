from django.urls import path
from .views import RegisterView, LoginView,CheckUsernameView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('check-username/', CheckUsernameView.as_view(), name='check-username'),
]
