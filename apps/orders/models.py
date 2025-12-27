from django.db import models
from django.core.validators import MinValueValidator


class Cart(models.Model):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='carts')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Cart {self.id}"

    def get_total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey('orders.Cart', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CartItem {self.id} - {self.product.title} - {self.quantity}"


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидание'
    PAID = 'paid', 'Оплачен'
    FAILED = 'failed', 'Неудачно'
    REFUNDED = 'refunded', 'Возвращен'
    CANCELLED = 'cancelled', 'Отменен'

class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Наличные'
    CREDIT_CARD = 'card', 'Карта'
    SBP = 'sbp', 'СБП'
    
class Payment(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Payment {self.id} - Order {self.order.id}"


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидание'
    PROCESSING = 'processing', 'В процессе'
    SHIPPED = 'shipped', 'Отправлен'
    DELIVERED = 'delivered', 'Доставлен'
    CANCELLED = 'cancelled', 'Отменен'
    COMPLETED = 'completed', 'Завершен'

class Order(models.Model):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"
    
    def get_total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem {self.id} - {self.product.title}"

