from django.contrib import admin
from .models import Documento, Anuncio, Categoria, Noticia

admin.site.register(Documento)
admin.site.register(Anuncio)
admin.site.register(Categoria)
admin.site.register(Noticia)