from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from equipos.models import CentroCosto, Division, Equipo, Sociedad


class Command(BaseCommand):
    help = 'Inicializa los grupos y permisos del sistema.'

    def handle(self, *args, **options):
        models = [Sociedad, Division, CentroCosto, Equipo]
        content_types = {model: ContentType.objects.get_for_model(model) for model in models}

        export_perm, _ = Permission.objects.get_or_create(
            codename='export_equipo',
            content_type=content_types[Equipo],
            defaults={'name': 'Puede exportar equipos'},
        )

        admin_group, _ = Group.objects.get_or_create(name='ADMIN')
        soporte_group, _ = Group.objects.get_or_create(name='SOPORTE')
        consulta_group, _ = Group.objects.get_or_create(name='CONSULTA')

        admin_permissions = Permission.objects.filter(
            content_type__app_label__in=['equipos', 'auth'],
        )
        admin_group.permissions.set(admin_permissions)

        soporte_permissions = []
        for model in models:
            base_codenames = ['view', 'add', 'change']
            if model in (Sociedad, Division, CentroCosto):
                base_codenames.append('delete')
            soporte_permissions.extend(
                Permission.objects.filter(
                    content_type=content_types[model],
                    codename__in=[f'{codename}_{model._meta.model_name}' for codename in base_codenames],
                )
            )
        if export_perm not in soporte_permissions:
            soporte_permissions.append(export_perm)
        soporte_group.permissions.set(soporte_permissions)

        consulta_permissions = []
        for model in models:
            consulta_permissions.extend(
                Permission.objects.filter(
                    content_type=content_types[model],
                    codename=f'view_{model._meta.model_name}',
                )
            )
        if export_perm not in consulta_permissions:
            consulta_permissions.append(export_perm)
        consulta_group.permissions.set(consulta_permissions)

        self.stdout.write(self.style.SUCCESS('Grupos y permisos inicializados.'))
