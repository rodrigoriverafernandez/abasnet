from django import forms
from .models import Documento, Anuncio


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'archivo', 'categoria', 'fecha_expiracion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del documento'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del documento', 'rows': 4}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'fecha_expiracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'archivo': 'Archivo',
            'categoria': 'Categoría',
            'fecha_expiracion': 'Fecha de Expiración',
        }


class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = ['titulo', 'contenido', 'categoria', 'fecha_expiracion', 'importancia']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del anuncio'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Contenido del anuncio', 'rows': 5}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'fecha_expiracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'importancia': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'titulo': 'Título',
            'contenido': 'Contenido',
            'categoria': 'Categoría',
            'fecha_expiracion': 'Fecha de Expiración',
            'importancia': 'Importancia',
        }