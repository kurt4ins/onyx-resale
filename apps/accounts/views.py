from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:profile')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация прошла успешно!')
        return response


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f'Добро пожаловать, {user.username}!')
        return super().form_valid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else self.success_url


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['get', 'post', 'options']
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):

    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context['customer'] = getattr(user, 'customer', None)
        context['seller'] = getattr(user, 'seller', None)
        
        return context
