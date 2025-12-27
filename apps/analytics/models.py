from django.db import models


class ProductView(models.Model):
    """Отслеживание просмотров товаров"""
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='views')
    customer = models.ForeignKey('accounts.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        verbose_name = "Просмотры товара"
        verbose_name_plural = "Просмотры товаров"
    
    def __str__(self):
        return f"View {self.id} - {self.product.title}"


class SearchQuery(models.Model):
    """Отслеживание поисковых запросов"""
    query = models.CharField(max_length=200)
    customer = models.ForeignKey('accounts.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    results_count = models.IntegerField(default=0, help_text="Количество найденных товаров")
    clicked_product = models.ForeignKey(
        'catalog.Product', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Товар, на который кликнули после поиска"
    )
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-searched_at']
        verbose_name = "Поисковый запрос"
        verbose_name_plural = "Поисковые запросы"
    
    def __str__(self):
        return f"Search: {self.query}"


class ProductAnalytics(models.Model):
    """Аналитика по конкретному товару"""
    product = models.OneToOneField('catalog.Product', on_delete=models.CASCADE, related_name='analytics')
    
    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    
    times_added_to_cart = models.IntegerField(default=0)
    times_added_to_wishlist = models.IntegerField(default=0)
    
    view_to_cart_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cart_to_purchase_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Аналитика товара"
        verbose_name_plural = "Аналитика товаров"
    
    def __str__(self):
        return f"Analytics for {self.product.title}"
