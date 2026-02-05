"""inventario URL Configuration."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from inventario import views

urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name='base.html')), name='inicio'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
]

handler403 = views.permission_denied
