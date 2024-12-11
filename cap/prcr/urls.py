from django.urls import path
from . import views

app_name = 'prcr'
urlpatterns = [
    # Category list view
    path('', views.CategoryListView.as_view(), name='main_list'),

    # Category and subcategory create views
    path('new_category', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/new_subcategory', views.SubcategoryCreateView.as_view(), name='subcategory_create'),

    # Brand create view
    path('new_brand', views.BrandCreateView.as_view(), name='brand_create'),

    # Brand list view
    path('brands', views.BrandListView.as_view(), name='brand_list'),

    # Feature create view
    path('product/<int:pk>/new_feature', views.FeatureCreateView.as_view(), name='feature_create'),

    # Price create view
    path('product/<int:pk>/new_price', views.PriceCreateView.as_view(), name='price_create'),

    # Product list view
    path('subcategory/<int:pk>/products', views.ProductListView.as_view(), name='product_list'),

    # Product detail, create and update views
    path('products/<int:pk>/detail', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/create', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/add_image', views.ProductAddImageView.as_view(), name='product_add_image'),

    # Product picture view
    path('picture/<int:pk>', views.stream_file, name='product_picture')
]