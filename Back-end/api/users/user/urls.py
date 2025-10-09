from django.urls import path, include
from .views import *

urlpatterns = [
    path('hello/', HelloView.as_view()),
    path('user/', UserView.as_view()),
    path('login/', LoginView.as_view()),
]
