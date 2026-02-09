from django.urls import path

from . import views


urlpatterns = [
    path("equipos/", views.equipos_list, name="equipos_list"),
    path("equipos/export/xlsx/", views.equipos_export_xlsx, name="equipos_export_xlsx"),
    path("equipos/<int:pk>/", views.equipo_detail, name="equipo_detail"),
    path("equipos/<int:pk>/editar/", views.equipo_editar, name="equipo_editar"),
    path("equipos/<int:pk>/baja/", views.equipo_baja, name="equipo_baja"),
    path("bajas/", views.bajas_list, name="bajas_list"),
    path("auditoria/", views.auditoria_list, name="auditoria_list"),
    path("reportes/", views.reportes_home, name="reportes_home"),
    path("reportes/inventario-activo/", views.reporte_inventario_activo, name="reporte_inventario_activo"),
    path("reportes/bajas/", views.reporte_equipos_baja, name="reporte_bajas"),
    path("reportes/equipos-baja/", views.reporte_equipos_baja, name="reporte_equipos_baja"),
    path("reportes/centro-costo/", views.reporte_centro_costo, name="reporte_centro_costo"),
    path("reportes/responsables/", views.reporte_responsables, name="reporte_responsables"),
    path("reportes/resumen/", views.reporte_resumen, name="reporte_resumen"),
]
