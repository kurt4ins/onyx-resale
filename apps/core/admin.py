from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Админка для уведомлений"""
    list_display = ('id', 'user', 'notification_type', 'title', 'is_read', 'created_at', 'read_at', 'delete_button')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    
    def delete_button(self, obj):
        """Кнопка удаления в списке"""
        if obj.pk:
            url = reverse('admin:core_notification_delete', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Удалить</a>',
                url
            )
        return '-'
    delete_button.short_description = 'Действия'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'notification_type', 'title', 'message', 'link')
        }),
        ('Статус', {
            'fields': ('is_read', 'read_at')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
