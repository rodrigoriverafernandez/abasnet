import csv
from datetime import datetime
import json

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from equipos.models import AuditLog, Equipo, ImportLog
from equipos.permissions import can_import
from django.db.models import Count
from inventario.importer import import_inventario_csv


def permission_denied(request, exception=None):
    return render(request, '403.html', status=403)


def _get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def _build_dashboard_context(request):
    total_equipos = Equipo.objects.count()
    total_bajas = Equipo.objects.filter(is_baja=True).count()
    total_activos = Equipo.objects.filter(is_baja=False).count()
    total_criticos = Equipo.objects.filter(infraestructura_critica=True).count()
    porcentaje_bajas = round((total_bajas / total_equipos) * 100, 2) if total_equipos else 0

    responsables_unicos = (
        Equipo.objects.exclude(rpe_responsable__isnull=True)
        .exclude(rpe_responsable__exact="")
        .values("rpe_responsable")
        .distinct()
        .count()
    )
    centros_unicos = (
        Equipo.objects.exclude(centro_costo__isnull=True)
        .values("centro_costo")
        .distinct()
        .count()
    )

    centros_qs = (
        Equipo.objects.exclude(centro_costo__isnull=True)
        .values("centro_costo__codigo", "centro_costo__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )
    centros_labels = [
        f"{item['centro_costo__codigo']} - {item['centro_costo__nombre']}" for item in centros_qs
    ]
    centros_totals = [item["total"] for item in centros_qs]

    marcas_qs = (
        Equipo.objects.exclude(marca__isnull=True)
        .values("marca__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )
    marcas_labels = [item["marca__nombre"] for item in marcas_qs]
    marcas_totals = [item["total"] for item in marcas_qs]

    sistemas_qs = (
        Equipo.objects.exclude(sistema_operativo__isnull=True)
        .values("sistema_operativo__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )
    sistemas_labels = [item["sistema_operativo__nombre"] for item in sistemas_qs]
    sistemas_totals = [item["total"] for item in sistemas_qs]

    import_model = _get_model("equipos", "ImportLog")
    baja_model = _get_model("equipos", "BajaEquipo")
    audit_model = _get_model("equipos", "AuditLog")

    import_logs = []
    if import_model:
        import_logs = (
            import_model.objects.select_related("usuario")
            .order_by("-fecha")[:5]
        )

    bajas = []
    if baja_model:
        bajas = (
            baja_model.objects.select_related("equipo", "usuario", "motivo")
            .order_by("-fecha_baja")[:10]
        )

    audit_logs = []
    if audit_model:
        audit_logs = (
            audit_model.objects.select_related("usuario")
            .order_by("-fecha")[:10]
        )

    return {
        "total_equipos": total_equipos,
        "total_activos": total_activos,
        "total_bajas": total_bajas,
        "total_criticos": total_criticos,
        "porcentaje_bajas": porcentaje_bajas,
        "responsables_unicos": responsables_unicos,
        "centros_unicos": centros_unicos,
        "chart_activos_bajas": json.dumps([total_activos, total_bajas]),
        "chart_activos_bajas_labels": json.dumps(["Activos", "Bajas"]),
        "chart_activos_bajas_total": total_equipos,
        "chart_centros_labels": json.dumps(centros_labels),
        "chart_centros_data": json.dumps(centros_totals),
        "centros_has_data": bool(centros_totals),
        "chart_marcas_labels": json.dumps(marcas_labels),
        "chart_marcas_data": json.dumps(marcas_totals),
        "marcas_has_data": bool(marcas_totals),
        "chart_sistemas_labels": json.dumps(sistemas_labels),
        "chart_sistemas_data": json.dumps(sistemas_totals),
        "sistemas_has_data": bool(sistemas_totals),
        "import_logs": import_logs,
        "bajas_recientes": bajas,
        "audit_logs": audit_logs,
        "mostrar_import_logs": bool(import_model),
        "mostrar_bajas": bool(baja_model),
        "mostrar_audit_logs": bool(audit_model),
        "fecha_actual": timezone.now(),
    }


@login_required
def inicio_dashboard(request):
    context = _build_dashboard_context(request)
    return render(request, "inicio_dashboard.html", context)

@login_required
def importar_inventario(request):
    if not can_import(request.user):
        return render(request, '403.html', status=403)

    context = {
        'modo': 'update_create',
        'resultados': None,
        'errores': [],
        'log_id': None,
    }

    if request.method == 'GET' and request.GET.get('download') == '1':
        log_id = request.GET.get('log_id')
        if not log_id:
            return HttpResponse('Falta el identificador del log.', status=400)
        try:
            log = ImportLog.objects.get(pk=log_id)
        except ImportLog.DoesNotExist:
            return HttpResponse('No se encontró el log solicitado.', status=404)
        return _export_errors_csv(log)

    if request.method == 'POST':
        modo = request.POST.get('modo', 'update_create')
        context['modo'] = modo
        path = settings.CSV_INVENTARIO_PATH
        resultados, errores = import_inventario_csv(path, modo)

        log = ImportLog.objects.create(
            usuario=request.user,
            archivo=str(path),
            total_filas=resultados['total'],
            creados=resultados['creados'],
            actualizados=resultados['actualizados'],
            omitidos=resultados['omitidos'],
            errores=resultados['errores'],
            resumen_errores=errores,
        )
        AuditLog.objects.create(
            usuario=request.user,
            accion='IMPORT',
            resumen=(
                'Importación CSV ejecutada. '
                f"Total: {resultados['total']}, "
                f"Creados: {resultados['creados']}, "
                f"Actualizados: {resultados['actualizados']}, "
                f"Omitidos: {resultados['omitidos']}, "
                f"Errores: {resultados['errores']}."
            ),
        )
        context['resultados'] = resultados
        context['errores'] = errores
        context['log_id'] = log.pk

    return render(request, 'importar.html', context)


def _export_errors_csv(log):
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="errores_importacion_{timestamp}.csv"'
    writer = csv.writer(response)
    writer.writerow(['fila', 'identificador', 'mensaje'])
    for error in log.resumen_errores or []:
        writer.writerow([error.get('fila'), error.get('identificador'), error.get('mensaje')])
    return response
