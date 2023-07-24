"""eform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
import os
import environ

env = environ.Env()
environ.Env.read_env()

schema_view = get_schema_view(
    openapi.Info(
        title="GIGAFORMS API", 
        default_version='v1',
        description="This GIGAFORMS API details",
        terms_of_service="https://epsumlabs.com",
        contact=openapi.Contact(email="surajkumar@epsumlabs.com"),
        license=openapi.License(name="BSD License")
    ),
    url= env("ALLOWED_URL"),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('user/', include('users.urls')),
    path('forms/', include('forms.urls')),
    path('workflow/', include('workflow.urls')),    
    path('fileupload/', include('fileupload.urls')),
    path('projects/', include('projects.urls')),
    path('organization/', include('organization.urls')),
    path('common/', include('commons.urls')),
    path('location/', include('location.urls')),        
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('logs/', include('systemlog.urls')),
    path('billings/', include('subscription.urls')),
    path('rozar/', include('payment_order.urls')), 
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)