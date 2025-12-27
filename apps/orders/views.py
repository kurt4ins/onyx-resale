from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from .models import Cart, CartItem, Order, OrderItem, Payment, PaymentStatus, OrderStatus
from apps.catalog.models import Product
from .forms import CheckoutForm


def get_or_create_cart(customer):
    cart, created = Cart.objects.get_or_create(customer=customer)
    return cart


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Необходимо войти в систему')
        return redirect('accounts:login')
    
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'Только клиенты могут добавлять товары в корзину')
        return redirect('catalog:product_list')
    
    product = get_object_or_404(Product, id=product_id, is_active=True, is_sold=False)
    customer = request.user.customer
    
    if product.quantity < 1:
        messages.error(request, 'Товар закончился')
        return redirect('catalog:product_detail', pk=product.id)
    
    cart = get_or_create_cart(customer)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'price': product.price, 'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < product.quantity:
            cart_item.quantity += 1
            cart_item.price = product.price
            cart_item.save()
            messages.success(request, f'Количество товара "{product.title}" увеличено')
        else:
            messages.warning(request, f'Максимальное количество товара "{product.title}" уже в корзине')
    else:
        messages.success(request, f'Товар "{product.title}" добавлен в корзину')
    
    return redirect('orders:cart')


def remove_from_cart(request, item_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'customer'):
        messages.error(request, 'Необходимо войти в систему')
        return redirect('accounts:login')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
    product_title = cart_item.product.title
    cart_item.delete()
    messages.success(request, f'Товар "{product_title}" удален из корзины')
    return redirect('orders:cart')


def update_cart_item(request, item_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'customer'):
        messages.error(request, 'Необходимо войти в систему')
        return redirect('accounts:login')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity < 1:
        cart_item.delete()
        messages.success(request, 'Товар удален из корзины')
    elif quantity > cart_item.product.quantity:
        messages.warning(request, f'Максимальное количество: {cart_item.product.quantity}')
    else:
        cart_item.quantity = quantity
        cart_item.price = cart_item.product.price
        cart_item.save()
        messages.success(request, 'Количество обновлено')
    
    return redirect('orders:cart')


class CartView(LoginRequiredMixin, ListView):
    template_name = 'orders/cart.html'
    context_object_name = 'cart_items'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'customer'):
            cart = get_or_create_cart(self.request.user.customer)
            return cart.items.select_related('product').prefetch_related('product__images')
        return CartItem.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'customer'):
            cart = get_or_create_cart(self.request.user.customer)
            context['cart'] = cart
            context['total_price'] = cart.get_total_price()
        return context


class CheckoutView(LoginRequiredMixin, FormView):
    form_class = CheckoutForm
    template_name = 'orders/checkout.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'customer'):
            messages.error(request, 'Только клиенты могут оформлять заказы')
            return redirect('accounts:profile')
        
        cart = get_or_create_cart(request.user.customer)
        if not cart.items.exists():
            messages.warning(request, 'Корзина пуста')
            return redirect('orders:cart')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['customer'] = self.request.user.customer
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request.user.customer)
        context['cart'] = cart
        context['cart_items'] = cart.items.select_related('product').prefetch_related('product__images')
        context['total_price'] = cart.get_total_price()
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        customer = self.request.user.customer
        cart = get_or_create_cart(customer)
        
        for item in cart.items.all():
            if item.product.quantity < item.quantity:
                messages.error(
                    self.request,
                    f'Товар "{item.product.title}" недоступен в количестве {item.quantity}'
                )
                return redirect('orders:cart')
            if item.product.is_sold or not item.product.is_active:
                messages.error(
                    self.request,
                    f'Товар "{item.product.title}" недоступен'
                )
                return redirect('orders:cart')
        
        order = Order.objects.create(
            customer=customer,
            status=OrderStatus.PENDING
        )
        
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price
            )
            item.product.quantity -= item.quantity
            if item.product.quantity == 0:
                item.product.is_sold = True
            item.product.save()
        
        total_price = cart.get_total_price()
        Payment.objects.create(
            order=order,
            status=PaymentStatus.PENDING,
            method=form.cleaned_data['payment_method'],
            amount=total_price
        )
        
        cart.items.all().delete()
        
        messages.success(self.request, f'Заказ #{order.id} успешно оформлен!')
        return redirect('orders:order_detail', pk=order.id)
    
    def get_success_url(self):
        return reverse_lazy('orders:order_list')


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'customer'):
            return Order.objects.filter(
                customer=self.request.user.customer
            ).prefetch_related('items__product', 'payments').order_by('-created_at')
        return Order.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_statuses'] = OrderStatus.choices
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'customer'):
            return Order.objects.filter(
                customer=self.request.user.customer
            ).prefetch_related('items__product__images', 'payments')
        return Order.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = self.object.get_total_price()
        return context
