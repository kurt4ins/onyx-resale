from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Customer, Seller
from .validators import normalize_phone


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('customer', 'Клиент'),
        ('seller', 'Продавец'),
    ]
    
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите имя пользователя'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Повторите пароль'
        })
    )
    role = forms.ChoiceField(
        label='Я хочу',
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'role-select'
        })
    )
    name = forms.CharField(
        label='Имя',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ваше имя'
        })
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+7 (999) 123-45-67'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'name', 'phone')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            return normalize_phone(phone)
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
            role = self.cleaned_data['role']
            name = self.cleaned_data['name']
            phone = self.cleaned_data['phone']
            
            if role == 'customer':
                Customer.objects.create(
                    user=user,
                    name=name,
                    email=user.email,
                    phone=phone
                )
            else:
                Seller.objects.create(
                    user=user,
                    name=name,
                    email=user.email,
                    phone=phone
                )
        
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        })
    )

