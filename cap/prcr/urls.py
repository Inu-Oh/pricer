from django.urls import path
from . import views

app_name = 'prcr'
urlpatterns = [
    # Category list view
    path('', views.CategoryListView.as_view(), name='main_list'),

    # Category and subcategory create views
    path('category/create', views.CategoryCreateView.as_view(), name='category_create'),
    path('subcategory/create', views.SubcategoryCreateView.as_view(), name='subcategory_create'),

    # Brand list view
    path('brands', views.BrandListView.as_view(), name='brand_list'),

    # Feature create view
    path('new_feature/<int:pk>', views.FeatureCreateView.as_view(), name='feature_form'),

    # Price create view
    path('new_price/<int:pk>', views.PriceCreateView.as_view(), name='price_form'),

    # Product list view
    path('products/<int:pk>', views.ProductListView.as_view(), name='product_list'),

    # Product detail, create and update views
    path('products/<int:pk>/detail', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/create', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update', views.ProductUpdateView.as_view(), name='product_update'),

    # Product picture view
    path('picture/<int:pk>', views.stream_file, name='product_picture')
]