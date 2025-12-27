from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Cart, CartItem, Payment, Order, OrderItem


class CartItemInline(admin.TabularInline):
    """Инлайн для элементов корзины"""
    model = CartItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('product', 'quantity', 'price', 'created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админка для корзин"""
    list_display = ('id', 'customer', 'created_at', 'updated_at', 'delete_button')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('customer__name', 'customer__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('customer',)
    inlines = [CartItemInline]
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:orders_cart_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     """Админка для элементов корзины"""
#     list_display = ('id', 'cart', 'product', 'quantity', 'price', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('cart__customer__name', 'product__title')
#     readonly_fields = ('created_at', 'updated_at')
#     raw_id_fields = ('cart', 'product')


class OrderItemInline(admin.TabularInline):
    """Инлайн для элементов заказа"""
    model = OrderItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('product', 'quantity', 'price', 'created_at', 'updated_at')


class PaymentInline(admin.TabularInline):
    """Инлайн для платежей"""
    model = Payment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('status', 'method', 'amount', 'created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов"""
    list_display = ('id', 'customer', 'status', 'created_at', 'updated_at', 'delete_button')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('customer__name', 'customer__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('customer',)
    inlines = [OrderItemInline, PaymentInline]
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:orders_order_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     """Админка для элементов заказа"""
#     list_display = ('id', 'order', 'product', 'quantity', 'price', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('order__customer__name', 'product__title')
#     readonly_fields = ('created_at', 'updated_at')
#     raw_id_fields = ('order', 'product')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админка для платежей"""
    list_display = ('id', 'order', 'status', 'method', 'amount', 'created_at', 'updated_at', 'delete_button')
    list_filter = ('status', 'method', 'created_at', 'updated_at')
    search_fields = ('order__customer__name', 'order__id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('order',)
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:orders_payment_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
