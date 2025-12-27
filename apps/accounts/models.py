from django.db import models
from django.contrib.auth.models import User
from .validators import validate_phone, normalize_phone


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=200, validators=[validate_phone])
    image = models.ImageField(upload_to='customers/', null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=200, validators=[validate_phone])
    image = models.ImageField(upload_to='sellers/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"

    def save(self, *args, **kwargs):
        """Нормализация телефона перед сохранением"""
        if self.phone:
            self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.email})"
