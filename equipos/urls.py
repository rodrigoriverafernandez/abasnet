from django.urls import path

from . import views


urlpatterns = [
    path("equipos/", views.equipos_list, name="equipos_list"),
    path("equipos/<int:pk>/", views.equipo_detail, name="equipo_detail"),
    path("equipos/<int:pk>/baja/", views.equipo_baja, name="equipo_baja"),
    path("bajas/", views.bajas_list, name="bajas_list"),
]
