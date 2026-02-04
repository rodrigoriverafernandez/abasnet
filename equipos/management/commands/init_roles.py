from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from equipos.models import Equipo


class Command(BaseCommand):
    help = 'Inicializa los grupos y permisos del sistema.'

    def handle(self, *args, **options):
        equipo_content_type = ContentType.objects.get_for_model(Equipo)

        import_perm, _ = Permission.objects.get_or_create(
            codename='import_equipo',
            content_type=equipo_content_type,
            defaults={'name': 'Puede importar equipos'},
        )
        export_perm, _ = Permission.objects.get_or_create(
            codename='export_equipo',
            content_type=equipo_content_type,
            defaults={'name': 'Puede exportar equipos'},
        )

        admin_group, _ = Group.objects.get_or_create(name='ADMIN')
        soporte_group, _ = Group.objects.get_or_create(name='SOPORTE')
        consulta_group, _ = Group.objects.get_or_create(name='CONSULTA')

        admin_group.permissions.set(Permission.objects.all())

        equipo_crud_perms = list(
            Permission.objects.filter(
                content_type=equipo_content_type,
                codename__in=['add_equipo', 'change_equipo', 'delete_equipo', 'view_equipo'],
            )
        )

        soporte_permissions = equipo_crud_perms[:]
        if import_perm not in soporte_permissions:
            soporte_permissions.append(import_perm)
        soporte_group.permissions.set(soporte_permissions)

        consulta_permissions = [
            perm for perm in equipo_crud_perms if perm.codename == 'view_equipo'
        ]
        if export_perm not in consulta_permissions:
            consulta_permissions.append(export_perm)
        consulta_group.permissions.set(consulta_permissions)

        self.stdout.write(self.style.SUCCESS('Grupos y permisos inicializados.'))
