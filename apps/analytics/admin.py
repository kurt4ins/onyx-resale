from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ProductView, SearchQuery, ProductAnalytics


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    """Админка для просмотров товаров"""
    list_display = ('id', 'product', 'customer', 'ip_address', 'viewed_at', 'delete_button')
    list_filter = ('viewed_at', 'product__category', 'product__seller')
    search_fields = ('product__title', 'customer__name', 'customer__email', 'ip_address')
    readonly_fields = ('viewed_at',)
    date_hierarchy = 'viewed_at'
    list_per_page = 50
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:analytics_productview_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    """Админка для поисковых запросов"""
    list_display = ('id', 'query', 'customer', 'results_count', 'clicked_product', 'searched_at', 'delete_button')
    list_filter = ('searched_at', 'results_count')
    search_fields = ('query', 'customer__name', 'customer__email', 'clicked_product__title')
    readonly_fields = ('searched_at',)
    date_hierarchy = 'searched_at'
    list_per_page = 50
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:analytics_searchquery_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'


@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    """Админка для аналитики товаров"""
    list_display = (
        'id', 
        'product', 
        'total_views', 
        'unique_views', 
        'times_added_to_cart', 
        'times_added_to_wishlist',
        'view_to_cart_rate',
        'cart_to_purchase_rate',
        'last_viewed_at',
        'updated_at',
        'delete_button'
    )
    list_filter = ('updated_at', 'last_viewed_at', 'product__category', 'product__seller')
    search_fields = ('product__title', 'product__seller__name')
    readonly_fields = ('updated_at',)
    date_hierarchy = 'updated_at'
    list_per_page = 50
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:analytics_productanalytics_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
    
    fieldsets = (
        ('Товар', {
            'fields': ('product',)
        }),
        ('Просмотры', {
            'fields': ('total_views', 'unique_views', 'last_viewed_at')
        }),
        ('Взаимодействия', {
            'fields': ('times_added_to_cart', 'times_added_to_wishlist')
        }),
        ('Конверсии', {
            'fields': ('view_to_cart_rate', 'cart_to_purchase_rate')
        }),
        ('Системная информация', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
