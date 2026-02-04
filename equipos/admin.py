from django.contrib import admin

from .models import CentroCosto, Division, Equipo, Sociedad


@admin.register(Sociedad)
class SociedadAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'sociedad')
    search_fields = ('codigo', 'nombre', 'sociedad__nombre')
    list_filter = ('sociedad',)


@admin.register(CentroCosto)
class CentroCostoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'division')
    search_fields = ('codigo', 'nombre', 'division__nombre')
    list_filter = ('division',)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'numero_serie', 'centro_costo', 'activo', 'creado_en')
    search_fields = ('nombre', 'numero_serie', 'centro_costo__nombre')
    list_filter = ('activo', 'centro_costo')
