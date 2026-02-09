from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from equipos.models import AuditLog, ImportLog
from inventario.importer import import_inventario_csv


class Command(BaseCommand):
    help = (
        "Ejecuta el backfill de numero_inventario desde el CSV usando numero_serie. "
        "Ejemplo: python manage.py fix_inventarios_from_csv --modo update_only"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--modo",
            choices=["update_create", "update_only", "create_only"],
            default="update_only",
            help="Modo de importación (por defecto: update_only).",
        )
        parser.add_argument(
            "--path",
            default=None,
            help="Ruta opcional al CSV (por defecto usa settings.CSV_INVENTARIO_PATH).",
        )

    def handle(self, *args, **options):
        modo = options["modo"]
        path = Path(options["path"]) if options["path"] else settings.CSV_INVENTARIO_PATH
        resultados, errores = import_inventario_csv(path, modo)

        log = ImportLog.objects.create(
            usuario=None,
            archivo=str(path),
            total_filas=resultados["total"],
            creados=resultados["creados"],
            actualizados=resultados["actualizados"],
            omitidos=resultados["omitidos"],
            errores=resultados["errores"],
            resumen_errores=errores,
        )
        AuditLog.objects.create(
            usuario=None,
            accion="IMPORT",
            resumen=(
                "Importación CSV ejecutada desde comando. "
                f"Total: {resultados['total']}, "
                f"Creados: {resultados['creados']}, "
                f"Actualizados: {resultados['actualizados']}, "
                f"Omitidos: {resultados['omitidos']}, "
                f"Errores: {resultados['errores']}."
            ),
        )

        self.stdout.write(self.style.SUCCESS("Importación finalizada."))
        self.stdout.write(
            f"Log ID: {log.pk} | Total: {resultados['total']} | "
            f"Actualizados: {resultados['actualizados']} | "
            f"Creados: {resultados['creados']} | "
            f"Errores: {resultados['errores']}"
        )
