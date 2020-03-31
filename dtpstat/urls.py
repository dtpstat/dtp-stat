"""dtpstat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from data import views as data_views

from rest_framework.routers import DefaultRouter
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'api/stat', data_views.StatApiView)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/dtp/', data_views.DTPApiView.as_view()),
    path('api/stat/', data_views.StatApiView.as_view({"get": "stat"})),
    path('api/filters/', data_views.FilterApiView.as_view()),
]

#urlpatterns += router.urls
