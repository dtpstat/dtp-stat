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
from django.urls import path, include
from data import views as data_views
from application import views as app_views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', app_views.home, name='home'),

    path('blog/', app_views.blog, name='blog'),
    path('blog/<slug>', app_views.blog_post, name='blog_post'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('pages/<slug>', app_views.page, name='page'),

    path('admin/', admin.site.urls),

    path('api/regions/', data_views.SearchRegionApiView.as_view()),
    path('api/dtp/', data_views.DTPApiView.as_view()),
    path('api/stat/', data_views.StatApiView.as_view({"get": "stat"})),
    path('api/filters/', data_views.FilterApiView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

