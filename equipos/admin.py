from django.contrib import admin

from .models import (
    AuditLog,
    BajaEquipo,
    CentroCosto,
    Division,
    Equipo,
    ImportLog,
    Marca,
    ModeloEquipo,
    SistemaOperativo,
    Sociedad,
    TipoEquipo,
)


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
    list_display = (
        'nombre',
        'identificador',
        'numero_inventario',
        'numero_serie',
        'centro_costo',
        'marca',
        'sistema_operativo',
        'activo',
        'is_baja',
        'fecha_baja',
        'creado_en',
    )
    search_fields = (
        'nombre',
        'identificador',
        'numero_inventario',
        'numero_serie',
        'centro_costo__nombre',
    )
    list_filter = ('activo', 'is_baja', 'centro_costo', 'marca', 'sistema_operativo', 'tipo_equipo')


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


@admin.register(SistemaOperativo)
class SistemaOperativoAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


@admin.register(TipoEquipo)
class TipoEquipoAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


@admin.register(ModeloEquipo)
class ModeloEquipoAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'archivo', 'total_filas', 'creados', 'actualizados', 'omitidos', 'errores')
    search_fields = ('archivo', 'usuario__username')
    list_filter = ('fecha',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion')
    search_fields = ('accion', 'usuario__username')


@admin.register(BajaEquipo)
class BajaEquipoAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'tipo_baja', 'fecha_baja')
    search_fields = ('equipo__identificador', 'equipo__numero_serie')
    list_filter = ('tipo_baja', 'fecha_baja')
