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
from application import views_api as api_views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', app_views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('board/', app_views.board, name='board'),
    path('board/feedback/', app_views.feedback_list, name='feedback_list'),

    path('dtp/<slug>/', app_views.dtp, name='dtp'),
    path('dtp/<slug>/fix_point/', app_views.dtp_fix_point, name='dtp_fix_point'),

    path('blog/', app_views.blog, name='blog'),
    path('blog/<slug>/', app_views.blog_post, name='blog_post'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('pages/<slug>/', app_views.page, name='page'),
    path('opendata/', app_views.opendata, name='opendata'),
    path('donate/', app_views.donate, name='donate'),

    path('admin/', admin.site.urls),

    path('api/dtp/', api_views.DTPApiView.as_view()),
    path('api/stat/', api_views.StatApiView.as_view({"get": "stat"})),
    path('api/filters/', api_views.FiltersApiView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

