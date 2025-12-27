from django.db import models


class NotificationType(models.TextChoices):
    ORDER_CREATED = 'order_created', 'Создан заказ'
    ORDER_STATUS = 'order_status', 'Изменен статус заказа'
    PAYMENT_RECEIVED = 'payment_received', 'Получен платеж'
    NEW_MESSAGE = 'new_message', 'Новое сообщение'
    PRODUCT_SOLD = 'product_sold', 'Товар продан'
    REVIEW_RECEIVED = 'review_received', 'Получен отзыв'

class Notification(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
