from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", include('prcr.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]
