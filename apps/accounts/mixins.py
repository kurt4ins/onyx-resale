from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin


class SellerRequiredMixin(LoginRequiredMixin):
    """Mixin для проверки, что пользователь является продавцом"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not hasattr(request.user, 'seller'):
            raise PermissionDenied("Доступ разрешен только продавцам")
        
        if not request.user.seller.is_active or request.user.seller.is_blocked:
            raise PermissionDenied("Ваш аккаунт продавца неактивен или заблокирован")
        
        return super().dispatch(request, *args, **kwargs)

