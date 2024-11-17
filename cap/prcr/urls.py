from django.urls import path
from . import views

app_name = 'prcr'
urlpatterns = [
    # Category list view
    path('', views.CategoryListView.as_view(), name='main_list'),
]