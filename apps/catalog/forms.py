from django import forms
from .models import Product, ProductImage, Category, Brand, Size


class ProductForm(forms.ModelForm):
    category_name = forms.CharField(
        label='Категория',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Начните вводить название категории...',
            'autocomplete': 'off',
            'id': 'category-autocomplete'
        })
    )
    
    brand_name = forms.CharField(
        label='Бренд',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Начните вводить название бренда...',
            'autocomplete': 'off',
            'id': 'brand-autocomplete'
        })
    )
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'size', 'custom_size',
            'price', 'quantity', 'condition', 'is_active', 'legit_check'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название товара'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 5,
                'placeholder': 'Описание товара'
            }),
            'size': forms.Select(attrs={'class': 'form-input'}),
            'custom_size': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Кастомный размер (если нужно)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0'
            }),
            'condition': forms.Select(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'legit_check': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['size'].queryset = Size.objects.all()
        self.fields['size'].required = False
        self.fields['custom_size'].required = False
        
        if self.instance and self.instance.pk:
            if self.instance.category:
                self.fields['category_name'].initial = self.instance.category.name
            if self.instance.brand:
                self.fields['brand_name'].initial = self.instance.brand.name
    
    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name', '').strip()
        if not category_name:
            return category_name
        
        try:
            category = Category.objects.get(name__iexact=category_name)
            return category_name
        except Category.DoesNotExist:
            from django.utils.text import slugify
            slug = slugify(category_name)
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{slugify(category_name)}-{counter}"
                counter += 1
            category = Category.objects.create(name=category_name, slug=slug)
            return category_name
    
    def clean_brand_name(self):
        brand_name = self.cleaned_data.get('brand_name', '').strip()
        if not brand_name:
            return brand_name
        
        try:
            brand = Brand.objects.get(name__iexact=brand_name)
            return brand_name
        except Brand.DoesNotExist:
            from django.utils.text import slugify
            slug = slugify(brand_name)
            counter = 1
            while Brand.objects.filter(slug=slug).exists():
                slug = f"{slugify(brand_name)}-{counter}"
                counter += 1
            brand = Brand.objects.create(name=brand_name, slug=slug)
            return brand_name
    
    def save(self, commit=True):
        product = super().save(commit=False)
        
        category_name = self.cleaned_data.get('category_name', '').strip()
        if category_name:
            try:
                product.category = Category.objects.get(name__iexact=category_name)
            except Category.DoesNotExist:
                pass
        
        brand_name = self.cleaned_data.get('brand_name', '').strip()
        if brand_name:
            try:
                product.brand = Brand.objects.get(name__iexact=brand_name)
            except Brand.DoesNotExist:
                pass
        
        if commit:
            product.save()
        return product


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'order', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0'
            }),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


ProductImageFormSet = forms.inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True
)


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название бренда'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
        }
    
    def save(self, commit=True):
        brand = super().save(commit=False)
        if not brand.slug:
            from django.utils.text import slugify
            brand.slug = slugify(brand.name)
        if commit:
            brand.save()
        return brand


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'size_type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название категории'
            }),
            'parent': forms.Select(attrs={'class': 'form-input'}),
            'size_type': forms.Select(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.all()
        self.fields['parent'].required = False
        self.fields['size_type'].required = False
    
    def save(self, commit=True):
        category = super().save(commit=False)
        if not category.slug:
            from django.utils.text import slugify
            base_slug = slugify(category.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            category.slug = slug
        if commit:
            category.save()
        return category


class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['size_type', 'value', 'display_value', 'us_size', 'eu_size', 'cm_size']
        widgets = {
            'size_type': forms.Select(attrs={'class': 'form-input'}),
            'value': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Значение размера'
            }),
            'display_value': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Отображаемое значение'
            }),
            'us_size': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'US размер (опционально)'
            }),
            'eu_size': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'EU размер (опционально)'
            }),
            'cm_size': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.1',
                'placeholder': 'Размер в см (опционально)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['us_size'].required = False
        self.fields['eu_size'].required = False
        self.fields['cm_size'].required = False

