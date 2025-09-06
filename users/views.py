from django.shortcuts import render
from .serializers import SingUpSerializer
from .models import CustomUser
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
# Create your views here.


class SingUpView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SingUpSerializer
    permission_classes = [AllowAny,]

