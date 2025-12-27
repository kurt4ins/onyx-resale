from django.urls import path
from .views import (
    CartView,
    add_to_cart,
    remove_from_cart,
    update_cart_item,
    CheckoutView,
    OrderListView,
    OrderDetailView
)

app_name = 'orders'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]

