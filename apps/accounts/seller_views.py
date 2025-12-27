from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.db.models import Count, Avg
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .mixins import SellerRequiredMixin
from apps.catalog.models import Product, Review, Brand, Category, Size
from apps.catalog.forms import (
    ProductForm, ProductImageFormSet, BrandForm, CategoryForm, SizeForm
)


class SellerPublicView(DetailView):
    template_name = 'accounts/seller_public.html'
    context_object_name = 'seller'
    pk_url_kwarg = 'seller_id'
    
    def get_queryset(self):
        from .models import Seller
        return Seller.objects.filter(is_active=True, is_blocked=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.get_object()
        
        products = Product.objects.filter(
            seller=seller,
            is_active=True,
            is_sold=False
        ).select_related('category', 'brand').prefetch_related('images')[:12]
        
        reviews = Review.objects.filter(
            seller=seller,
            is_approved=True
        ).select_related('customer').order_by('-created_at')[:5]
        
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        context['products'] = products
        context['reviews'] = reviews
        context['avg_rating'] = round(avg_rating, 1)
        context['total_products'] = Product.objects.filter(seller=seller, is_active=True).count()
        
        return context


class SellerDashboardView(SellerRequiredMixin, TemplateView):
    template_name = 'accounts/seller_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.request.user.seller
        
        total_products = Product.objects.filter(seller=seller).count()
        active_products = Product.objects.filter(seller=seller, is_active=True, is_sold=False).count()
        sold_products = Product.objects.filter(seller=seller, is_sold=True).count()
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_products = Product.objects.filter(
            seller=seller,
            created_at__gte=thirty_days_ago
        ).count()
        
        reviews = Review.objects.filter(seller=seller, is_approved=True)
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        recent_products_list = Product.objects.filter(
            seller=seller
        ).select_related('category', 'brand').prefetch_related('images').order_by('-created_at')[:5]
        
        context.update({
            'seller': seller,
            'total_products': total_products,
            'active_products': active_products,
            'sold_products': sold_products,
            'recent_products': recent_products,
            'total_reviews': total_reviews,
            'avg_rating': round(avg_rating, 1),
            'recent_products_list': recent_products_list,
        })
        
        return context


class SellerProductListView(SellerRequiredMixin, ListView):
    model = Product
    template_name = 'accounts/seller_products.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        seller = self.request.user.seller
        queryset = Product.objects.filter(seller=seller).select_related(
            'category', 'brand'
        ).prefetch_related('images').order_by('-created_at')
        
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True, is_sold=False)
        elif status == 'sold':
            queryset = queryset.filter(is_sold=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class SellerProductCreateView(SellerRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'accounts/seller_product_form.html'
    
    def form_valid(self, form):
        form.instance.seller = self.request.user.seller
        response = super().form_valid(form)
        
        formset = ProductImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
            if not self.object.images.filter(is_main=True).exists():
                first_image = self.object.images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
        
        messages.success(self.request, 'Товар успешно создан!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = ProductImageFormSet()
        return context
    
    def get_success_url(self):
        return reverse_lazy('accounts:seller_products')


class SellerProductUpdateView(SellerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'accounts/seller_product_form.html'
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user.seller)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        formset = ProductImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        if formset.is_valid():
            formset.save()
        
        messages.success(self.request, 'Товар успешно обновлен!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['formset'] = ProductImageFormSet(instance=self.object)
        return context
    
    def get_success_url(self):
        return reverse_lazy('accounts:seller_products')


class SellerProductDeleteView(SellerRequiredMixin, DeleteView):
    model = Product
    template_name = 'accounts/seller_product_confirm_delete.html'
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user.seller)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Товар успешно удален!')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('accounts:seller_products')


class SellerStatsView(SellerRequiredMixin, TemplateView):
    template_name = 'accounts/seller_stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.request.user.seller
        
        total_products = Product.objects.filter(seller=seller).count()
        active_products = Product.objects.filter(seller=seller, is_active=True, is_sold=False).count()
        sold_products = Product.objects.filter(seller=seller, is_sold=True).count()
        
        category_stats = Product.objects.filter(seller=seller).values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        brand_stats = Product.objects.filter(seller=seller).values(
            'brand__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        monthly_stats = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            count = Product.objects.filter(
                seller=seller,
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_stats.append({
                'month': month_start.strftime('%B %Y'),
                'count': count
            })
        monthly_stats.reverse()
        
        reviews = Review.objects.filter(seller=seller, is_approved=True)
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        rating_distribution = reviews.values('rating').annotate(count=Count('id')).order_by('rating')
        
        context.update({
            'seller': seller,
            'total_products': total_products,
            'active_products': active_products,
            'sold_products': sold_products,
            'category_stats': category_stats,
            'brand_stats': brand_stats,
            'monthly_stats': monthly_stats,
            'total_reviews': total_reviews,
            'avg_rating': round(avg_rating, 1),
            'rating_distribution': rating_distribution,
        })
        
        return context


class SellerBrandCreateView(SellerRequiredMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'accounts/seller_reference_form.html'
    success_url = reverse_lazy('accounts:seller_references')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать бренд'
        context['reference_type'] = 'brand'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Бренд успешно создан!')
        return super().form_valid(form)


class SellerCategoryCreateView(SellerRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'accounts/seller_reference_form.html'
    success_url = reverse_lazy('accounts:seller_references')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать категорию'
        context['reference_type'] = 'category'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Категория успешно создана!')
        return super().form_valid(form)


class SellerSizeCreateView(SellerRequiredMixin, CreateView):
    model = Size
    form_class = SizeForm
    template_name = 'accounts/seller_reference_form.html'
    success_url = reverse_lazy('accounts:seller_references')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать размер'
        context['reference_type'] = 'size'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Размер успешно создан!')
        return super().form_valid(form)


class SellerReferencesView(SellerRequiredMixin, TemplateView):
    template_name = 'accounts/seller_references.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all().order_by('name')
        context['categories'] = Category.objects.filter(parent=None).order_by('name')
        context['sizes'] = Size.objects.all().order_by('size_type', 'value')
        return context

