from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Customer, Seller


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'user', 'date_created', 'delete_button')
    list_filter = ('date_created',)
    search_fields = ('name', 'email', 'phone', 'user__username')
    readonly_fields = ('date_created',)
    date_hierarchy = 'date_created'
    raw_id_fields = ('user',)
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:accounts_customer_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
    
    def delete_model(self, request, obj):
        """Кастомное удаление с предупреждением"""
        from django.contrib import messages
        from apps.orders.models import Order, Cart
        from apps.catalog.models import Wishlist
        
        order_count = Order.objects.filter(customer=obj).count()
        cart_count = Cart.objects.filter(customer=obj).count()
        wishlist_count = Wishlist.objects.filter(customer=obj).count()
        
        if order_count > 0 or cart_count > 0 or wishlist_count > 0:
            messages.warning(
                request,
                f'Внимание! У клиента "{obj.name}" есть связанные данные: '
                f'{order_count} заказов, {cart_count} корзин, {wishlist_count} избранных товаров. '
                f'Они также будут удалены.'
            )
        
        super().delete_model(request, obj)


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'user', 'is_active', 'is_verified', 'is_blocked', 'date_created', 'delete_button')
    list_filter = ('is_active', 'is_verified', 'is_blocked', 'date_created')
    search_fields = ('name', 'email', 'phone', 'user__username')
    readonly_fields = ('date_created',)
    date_hierarchy = 'date_created'
    raw_id_fields = ('user',)
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:accounts_seller_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
    
    def delete_model(self, request, obj):
        """Кастомное удаление с предупреждением о товарах"""
        from django.contrib import messages
        from apps.catalog.models import Product, Review
        
        product_count = Product.objects.filter(seller=obj).count()
        review_count = Review.objects.filter(seller=obj).count()
        
        if product_count > 0 or review_count > 0:
            messages.warning(
                request,
                f'Внимание! У продавца "{obj.name}" есть связанные данные: '
                f'{product_count} товаров, {review_count} отзывов. '
                f'Они также будут удалены.'
            )
        
        super().delete_model(request, obj)
