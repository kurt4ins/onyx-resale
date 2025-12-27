from django.db import models
from django.core.validators import MinValueValidator


class Wishlist(models.Model):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'product']
        ordering = ['-added_at']
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
    
    def __str__(self):
        return f"{self.customer.name} - {self.product.title}"
        

class SizeType(models.TextChoices):
    CLOTHING = 'clothing', 'Одежда'
    SHOES = 'shoes', 'Обувь'
    ACCESSORIES = 'accessories', 'Аксессуары'


class Size(models.Model):
    size_type = models.CharField(max_length=20, choices=SizeType.choices)
    
    value = models.CharField(max_length=20)  # Основное значение размера
    display_value = models.CharField(max_length=20)  # Отображаемое значение
    
    us_size = models.CharField(max_length=10, blank=True, null=True)
    eu_size = models.CharField(max_length=10, blank=True, null=True)
    cm_size = models.DecimalField(
        max_digits=5, 
        decimal_places=1, 
        blank=True, 
        null=True,
        help_text="Размер в сантиметрах (для обуви - длина стопы)"
    )
    
    class Meta:
        unique_together = ['size_type', 'value']
        ordering = ['size_type', 'value']
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
    
    def __str__(self):
        return f"{self.get_size_type_display()}: {self.display_value}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    size_type = models.CharField(
        max_length=20,
        choices=SizeType.choices,
        null=True,
        blank=True,
        help_text="Тип размера для этой категории"
    )
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


class ProductCondition(models.TextChoices):
    NEW = 'new', 'Новое с биркой'
    EXCELLENT = 'excellent', 'Отличное'
    GOOD = 'good', 'Хорошее'
    FAIR = 'fair', 'Удовлетворительное'


class Product(models.Model):
    seller = models.ForeignKey('accounts.Seller', on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, related_name='products')
    
    custom_size = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Кастомный размер, если не подходит стандартный"
    )
    
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=0)
    condition = models.CharField(max_length=20, choices=ProductCondition.choices)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    legit_check = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    
    @property
    def display_size(self):
        if self.custom_size:
            return self.custom_size
        if self.size:
            return self.size.display_value
        return "Не указан"
    
    def __str__(self):
        return f"{self.title} - {self.display_size}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')
    order = models.PositiveIntegerField(default=0, help_text="Порядок отображения")
    is_main = models.BooleanField(default=False, help_text="Главное изображение")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
    
    def __str__(self):
        return f"Изображение {self.id} для {self.product.title}"


class Review(models.Model):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='reviews')
    seller = models.ForeignKey('accounts.Seller', on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    rating = models.IntegerField(default=0)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
