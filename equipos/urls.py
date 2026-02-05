from django.urls import path

from . import views


urlpatterns = [
    path("equipos/", views.equipos_list, name="equipos_list"),
    path("equipos/<int:pk>/", views.equipo_detail, name="equipo_detail"),
    path("equipos/<int:pk>/baja/", views.equipo_baja, name="equipo_baja"),
    path("bajas/", views.bajas_list, name="bajas_list"),
    path("reportes/", views.reportes_home, name="reportes_home"),
    path("reportes/inventario-activo/", views.reporte_inventario_activo, name="reporte_inventario_activo"),
    path("reportes/equipos-baja/", views.reporte_equipos_baja, name="reporte_equipos_baja"),
    path("reportes/resumen/", views.reporte_resumen, name="reporte_resumen"),
]
