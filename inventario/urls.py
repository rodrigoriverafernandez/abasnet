"""inventario URL Configuration."""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='base.html'), name='inicio'),
    path('admin/', admin.site.urls),
]
