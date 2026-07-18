from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, ClientViewSet

# The router automatically creates all the necessary endpoints
router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]