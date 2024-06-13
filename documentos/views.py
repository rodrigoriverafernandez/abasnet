from django.shortcuts import render, get_object_or_404, redirect
from .models import Documento, Anuncio, Noticia
from django.contrib.auth.decorators import login_required
from .forms import DocumentoForm, AnuncioForm
from django.db.models import Q
from django.core.paginator import Paginator

def inicio(request):
    noticias_generales = Noticia.objects.filter(categoria='general').order_by('-fecha_publicacion')[:3]
    noticias_gerencia = Noticia.objects.filter(categoria='gerencia').order_by('-fecha_publicacion')[:3]
    noticias_recursos_humanos = Noticia.objects.filter(categoria='recursos_humanos').order_by('-fecha_publicacion')[:3]
    return render(request, 'index.html', {
        'noticias_generales': noticias_generales,
        'noticias_gerencia': noticias_gerencia,
        'noticias_recursos_humanos': noticias_recursos_humanos,
    })

def noticias(request):
    noticias_generales = Noticia.objects.filter(categoria='general').order_by('-fecha_publicacion')
    noticias_gerencia = Noticia.objects.filter(categoria='gerencia').order_by('-fecha_publicacion')
    noticias_recursos_humanos = Noticia.objects.filter(categoria='recursos_humanos').order_by('-fecha_publicacion')
    return render(request, 'documentos/noticias.html', {
        'noticias_generales': noticias_generales,
        'noticias_gerencia': noticias_gerencia,
        'noticias_recursos_humanos': noticias_recursos_humanos,
    })


@login_required
def lista_documentos(request):
    query = request.GET.get('q')
    if query:
        documentos_list = Documento.objects.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query)
        )
    else:
        documentos_list = Documento.objects.all()

    paginator = Paginator(documentos_list, 6)  # Mostrar 10 documentos por página
    page_number = request.GET.get('page')
    documentos = paginator.get_page(page_number)

    return render(request, 'documentos/lista_documentos.html', {'documentos': documentos, 'query': query})
   
@login_required
def detalle_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    return render(request, 'documentos/detalle_documento.html', {'documento': documento})

@login_required
def lista_anuncios(request):
    anuncios = Anuncio.objects.all()
    return render(request, 'documentos/lista_anuncios.html', {'anuncios': anuncios})

@login_required
def detalle_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    return render(request, 'documentos/detalle_anuncio.html', {'anuncio': anuncio})

@login_required
def subir_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.autor = request.user  # Asigna el autor como el usuario autenticado
            documento.save()
            return redirect('lista_documentos')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/subir_documento.html', {'form': form})

@login_required
def subir_anuncio(request):
    if request.method == 'POST':
        form = AnuncioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_anuncios')
    else:
        form = AnuncioForm()
    return render(request, 'documentos/subir_anuncio.html', {'form': form})

def detalle_noticia(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    return render(request, 'documentos/detalle_noticia.html', {'noticia': noticia})




def acerca_de(request):
    return render(request, 'documentos/acerca_de.html')

def contacto(request):
    return render(request, 'documentos/contacto.html')

def politicas(request):
    return render(request, 'documentos/politicas.html')
