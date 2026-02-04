"""ASGI config for inventario project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario.settings')

application = get_asgi_application()
