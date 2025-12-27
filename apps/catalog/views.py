from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category, Brand, Wishlist


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 24
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, is_sold=False).select_related(
            'category', 'brand', 'seller'
        ).prefetch_related('images')
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query)
            )
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        sort_by = self.request.GET.get('sort', 'created_at')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_condition'] = self.request.GET.get('condition', '')
        context['sort_by'] = self.request.GET.get('sort', 'created_at')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand', 'seller'
        ).prefetch_related('images', 'reviews')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        in_wishlist = False
        if self.request.user.is_authenticated and hasattr(self.request.user, 'customer'):
            in_wishlist = Wishlist.objects.filter(
                customer=self.request.user.customer,
                product=product
            ).exists()
        
        context['in_wishlist'] = in_wishlist
        
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True,
            is_sold=False
        ).exclude(id=product.id)[:4]
        context['similar_products'] = similar_products
        
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(parent=None)


class BrandListView(ListView):
    model = Brand
    template_name = 'catalog/brand_list.html'
    context_object_name = 'brands'


class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'catalog/wishlist.html'
    context_object_name = 'wishlist_items'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'customer'):
            return Wishlist.objects.filter(
                customer=self.request.user.customer
            ).select_related('product').prefetch_related('product__images')
        return Wishlist.objects.none()


def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Необходимо войти в систему')
        return redirect('accounts:login')
    
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'Только клиенты могут добавлять товары в избранное')
        return redirect('catalog:product_list')
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    customer = request.user.customer
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        customer=customer,
        product=product
    )
    
    if not created:
        wishlist_item.delete()
        messages.success(request, 'Товар удален из избранного')
    else:
        messages.success(request, 'Товар добавлен в избранное')
    
    return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list'))


def autocomplete_category(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    categories = Category.objects.filter(name__icontains=query)[:10]
    results = [{'id': cat.id, 'text': cat.name} for cat in categories]
    return JsonResponse({'results': results})


def autocomplete_brand(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    brands = Brand.objects.filter(name__icontains=query)[:10]
    results = [{'id': brand.id, 'text': brand.name} for brand in brands]
    return JsonResponse({'results': results})
