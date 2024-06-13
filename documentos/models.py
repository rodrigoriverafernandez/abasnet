from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Documento(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='documentos/')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.titulo




class Anuncio(models.Model):
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Asegúrate de que el usuario con id=1 existe
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateField(null=True, blank=True)
    importancia = models.CharField(max_length=50, choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')], default='Media')

    def __str__(self):
        return self.titulo
    


   

from django.db import models

from ckeditor.fields import RichTextField

from django.db import models
from ckeditor.fields import RichTextField

class Noticia(models.Model):
    CATEGORIAS = [
        ('general', 'General'),
        ('gerencia', 'Gerencia'),
        ('recursos_humanos', 'Recursos Humanos'),
    ]

    titulo = models.CharField(max_length=255)
    contenido = RichTextField()
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='general')

    def __str__(self):
        return self.titulo
