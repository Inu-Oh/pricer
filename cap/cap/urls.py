import os

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path("", include('prcr.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
]

# Serve the static HTML
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urlpatterns += [
    re_path(r'^site/(?P<path>.*)$', serve,
        {'document_root': os.path.join(BASE_DIR, 'site'),
         'show_indexes': True},
        name='site_path'
        ),
]

# Serve the favicon
urlpatterns += [
    path('favicon.ico', serve, {
        'path': 'favicon.ico',
        'document_root': os.path.join(BASE_DIR, 'home/static')
    }),
]
