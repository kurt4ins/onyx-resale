from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
    BrandListView,
    WishlistView,
    toggle_wishlist,
    autocomplete_category,
    autocomplete_brand
)

app_name = 'catalog'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('brands/', BrandListView.as_view(), name='brand_list'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', toggle_wishlist, name='toggle_wishlist'),
    path('autocomplete/category/', autocomplete_category, name='autocomplete_category'),
    path('autocomplete/brand/', autocomplete_brand, name='autocomplete_brand'),
]

