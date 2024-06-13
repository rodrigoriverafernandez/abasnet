from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('documentos/', views.lista_documentos, name='lista_documentos'),
    path('documentos/<int:pk>/', views.detalle_documento, name='detalle_documento'),
    path('anuncios/', views.lista_anuncios, name='lista_anuncios'),
    path('anuncios/<int:pk>/', views.detalle_anuncio, name='detalle_anuncio'),
    path('subir_documento/', views.subir_documento, name='subir_documento'),
    path('subir_anuncio/', views.subir_anuncio, name='subir_anuncio'),
    path('noticias/<int:pk>/', views.detalle_noticia, name='detalle_noticia'),
    path('acerca_de/', views.acerca_de, name='acerca_de'),
    path('contacto/', views.contacto, name='contacto'),
    path('politicas/', views.politicas, name='politicas'),
    path('noticias/', views.noticias, name='noticias'),  # Nueva URL para la página de noticias
    path('noticias/<int:pk>/', views.detalle_noticia, name='detalle_noticia'),
]
