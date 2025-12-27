from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogoutView, ProfileView
from .seller_views import (
    SellerPublicView,
    SellerDashboardView,
    SellerProductListView,
    SellerProductCreateView,
    SellerProductUpdateView,
    SellerProductDeleteView,
    SellerStatsView,
    SellerReferencesView,
    SellerBrandCreateView,
    SellerCategoryCreateView,
    SellerSizeCreateView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Публичная страница продавца
    path('seller/<int:seller_id>/', SellerPublicView.as_view(), name='seller_public'),
    
    # Личный кабинет продавца (только для продавцов)
    path('seller/dashboard/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('seller/products/', SellerProductListView.as_view(), name='seller_products'),
    path('seller/products/create/', SellerProductCreateView.as_view(), name='seller_product_create'),
    path('seller/products/<int:pk>/edit/', SellerProductUpdateView.as_view(), name='seller_product_edit'),
    path('seller/products/<int:pk>/delete/', SellerProductDeleteView.as_view(), name='seller_product_delete'),
    path('seller/stats/', SellerStatsView.as_view(), name='seller_stats'),
    path('seller/references/', SellerReferencesView.as_view(), name='seller_references'),
    path('seller/references/brand/create/', SellerBrandCreateView.as_view(), name='seller_brand_create'),
    path('seller/references/category/create/', SellerCategoryCreateView.as_view(), name='seller_category_create'),
    path('seller/references/size/create/', SellerSizeCreateView.as_view(), name='seller_size_create'),
]

