from django.shortcuts import render
from rest_framework import viewsets
from .models import Company, Client
from .serializers import CompanySerializer, ClientSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer