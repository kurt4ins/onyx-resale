from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from .models import Wishlist, Size, Category, Brand, Product, ProductImage, Review


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    """Админка для размеров"""
    list_display = ('id', 'size_type', 'value', 'display_value', 'us_size', 'eu_size', 'cm_size', 'delete_button')
    list_filter = ('size_type',)
    search_fields = ('value', 'display_value', 'us_size', 'eu_size')
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:catalog_size_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    list_display = ('id', 'name', 'slug', 'parent', 'size_type', 'delete_button')
    list_filter = ('size_type', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('parent',)
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:catalog_category_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
    
    def delete_model(self, request, obj):
        """Кастомное удаление с предупреждением о дочерних категориях"""
        from django.contrib import messages
        
        # Проверяем наличие дочерних категорий
        child_count = Category.objects.filter(parent=obj).count()
        if child_count > 0:
            messages.warning(
                request, 
                f'Внимание! У категории "{obj.name}" есть {child_count} дочерних категорий. '
                f'Они также будут удалены вместе с этой категорией.'
            )
        
        # Проверяем наличие товаров в этой категории
        from .models import Product
        product_count = Product.objects.filter(category=obj).count()
        if product_count > 0:
            messages.warning(
                request,
                f'Внимание! В категории "{obj.name}" есть {product_count} товаров. '
                f'Они не будут удалены, но останутся без категории.'
            )
        
        super().delete_model(request, obj)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Админка для брендов"""
    list_display = ('id', 'name', 'slug', 'delete_button')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:catalog_brand_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
    
    def delete_model(self, request, obj):
        """Кастомное удаление с предупреждением о товарах"""
        from django.contrib import messages
        from .models import Product
        
        product_count = Product.objects.filter(brand=obj).count()
        if product_count > 0:
            messages.warning(
                request,
                f'Внимание! У бренда "{obj.name}" есть {product_count} товаров. '
                f'Они не будут удалены, но останутся без бренда.'
            )
        
        super().delete_model(request, obj)


class ProductImageInline(admin.TabularInline):
    """Инлайн для изображений товара"""
    model = ProductImage
    extra = 1
    fields = ('image', 'order', 'is_main')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для товаров"""
    list_display = (
        'id', 'title', 'seller', 'category', 'brand', 'price', 
        'quantity', 'condition', 'is_active', 'is_sold', 
        'legit_check', 'created_at', 'delete_button'
    )
    list_filter = ('is_active', 'is_sold', 'legit_check', 'condition', 'category', 'brand', 'created_at')
    search_fields = ('title', 'description', 'seller__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('seller', 'category', 'brand', 'size')
    inlines = [ProductImageInline]
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:catalog_product_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('seller', 'title', 'description', 'category', 'brand')
        }),
        ('Размер', {
            'fields': ('size', 'custom_size')
        }),
        ('Цена и количество', {
            'fields': ('price', 'quantity', 'condition')
        }),
        ('Статусы', {
            'fields': ('is_active', 'is_sold', 'legit_check')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_deleted_objects(self, objs, request):
        """Показывает связанные объекты, которые будут удалены"""
        from django.contrib.admin.utils import NestedObjects
        from django.db import router
        
        collector = NestedObjects(using=router.db_for_write(objs[0]))
        collector.collect(objs)
        
        to_delete = collector.nested()
        protected = collector.protected
        model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
        
        return to_delete, model_count, protected


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Админка для изображений товаров"""
    list_display = ('id', 'product', 'order', 'is_main', 'created_at', 'delete_button')
    list_filter = ('is_main', 'created_at')
    search_fields = ('product__title',)
    raw_id_fields = ('product',)
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:catalog_productimage_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Админка для избранного"""
    list_display = ('id', 'customer', 'product', 'added_at', 'delete_button')
    list_filter = ('added_at',)
    search_fields = ('customer__name', 'product__title')
    date_hierarchy = 'added_at'
    raw_id_fields = ('customer', 'product')
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:catalog_wishlist_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для отзывов"""
    list_display = ('id', 'customer', 'seller', 'rating', 'is_approved', 'created_at', 'delete_button')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('customer__name', 'seller__name', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    raw_id_fields = ('customer', 'seller')
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:catalog_review_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
