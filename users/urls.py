from .views import SingUpView
from django.urls import path

urlpatterns = [
    path('singup/', SingUpView.as_view())
]