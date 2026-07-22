from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CashflowForecastView, DocumentViewSet, SpreadsheetImportViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'spreadsheets', SpreadsheetImportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('forecast/', CashflowForecastView.as_view(), name='cashflow-forecast'),
]
