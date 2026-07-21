"""
URL configuration for fawatir_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core API endpoints routed from the 'api' app
    path('api/', include('api.urls')),
    
    # OpenAPI Schema generator endpoint
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI documentation endpoint
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]