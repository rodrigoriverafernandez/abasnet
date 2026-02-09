import csv
from datetime import datetime
import json
import unicodedata

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from equipos.models import (
    AuditLog,
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
from equipos.permissions import can_import
from django.db.models import Count
ERRORS_LIMIT = 50


def _normalize_value(value):
    if value is None:
        return ''
    cleaned = unicodedata.normalize('NFKC', str(value)).strip()
    if cleaned.lower() in {'no disponible', 'no aplica', 'n/a', 'na'}:
        return ''
    return cleaned


def _get_row_value(row, *keys):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return ''


def _normalize_header(value):
    cleaned = str(value).strip().replace('*', '').lower()
    return ''.join(
        char for char in unicodedata.normalize('NFKD', cleaned) if not unicodedata.combining(char)
    )


def _get_row_value_by_headers(row, headers):
    if not row:
        return ''
    normalized_map = {_normalize_header(key): value for key, value in row.items()}
    for header in headers:
        if header in row and row[header] is not None:
            return row[header]
        normalized_header = _normalize_header(header)
        if normalized_header in normalized_map and normalized_map[normalized_header] is not None:
            return normalized_map[normalized_header]
    return ''


def _get_or_create_catalog(model, value):
    cleaned = _normalize_value(value)
    if not cleaned:
        return None
    obj, _ = model.objects.get_or_create(nombre=cleaned)
    return obj


def _parse_boolean(value):
    cleaned = _normalize_value(value)
    if not cleaned:
        return False
    normalized = ''.join(
        char for char in unicodedata.normalize('NFKD', cleaned) if not unicodedata.combining(char)
    ).lower()
    return normalized in {"si", "sí", "s", "true", "1", "x", "yes"}


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
        resultados = {
            'total': 0,
            'creados': 0,
            'actualizados': 0,
            'omitidos': 0,
            'errores': 0,
        }
        errores = []
        path = settings.CSV_INVENTARIO_PATH
        if not path.exists():
            errores.append({'fila': '-', 'identificador': '-', 'mensaje': 'No se encontró el archivo CSV.'})
        else:
            with open(path, encoding='utf-8', errors='replace', newline='') as archivo:
                lector = csv.DictReader(archivo)
                for numero_fila, row in enumerate(lector, start=2):
                    resultados['total'] += 1
                    try:
                        inventario = _normalize_value(
                            _get_row_value_by_headers(
                                row,
                                [
                                    'Número de inventario*',
                                    'Numero de inventario*',
                                    'Número de inventario',
                                    'Numero de inventario',
                                ],
                            )
                        )
                        clave = _normalize_value(_get_row_value(row, 'Clave', '\ufeffClave'))
                        identificador = inventario or clave
                        if not identificador:
                            raise ValueError('Identificador vacío (Número de inventario* o Clave).')

                        nombre_equipo = _normalize_value(_get_row_value(row, 'Nombre')) or identificador
                        numero_serie = _normalize_value(_get_row_value(row, 'Número de serie*'))
                        if not numero_serie:
                            raise ValueError('Número de serie vacío.')

                        sociedad_codigo = _normalize_value(_get_row_value(row, 'Sociedad'))
                        sociedad_nombre = _normalize_value(_get_row_value(row, 'Nombre de Sociedad')) or sociedad_codigo
                        if not sociedad_codigo:
                            raise ValueError('Sociedad vacía.')
                        sociedad, _ = Sociedad.objects.get_or_create(
                            codigo=sociedad_codigo,
                            defaults={'nombre': sociedad_nombre or sociedad_codigo},
                        )
                        if sociedad_nombre and sociedad.nombre != sociedad_nombre:
                            sociedad.nombre = sociedad_nombre
                            sociedad.save(update_fields=['nombre'])

                        division_codigo = _normalize_value(_get_row_value(row, 'División'))
                        division_nombre = _normalize_value(_get_row_value(row, 'Nombre de División')) or division_codigo
                        if not division_codigo:
                            raise ValueError('División vacía.')
                        division, _ = Division.objects.get_or_create(
                            sociedad=sociedad,
                            codigo=division_codigo,
                            defaults={'nombre': division_nombre or division_codigo},
                        )
                        if division_nombre and division.nombre != division_nombre:
                            division.nombre = division_nombre
                            division.save(update_fields=['nombre'])

                        centro_codigo = _normalize_value(_get_row_value(row, 'Centro de Costo'))
                        centro_nombre = centro_codigo
                        if not centro_codigo:
                            raise ValueError('Centro de costo vacío.')
                        centro_costo, _ = CentroCosto.objects.get_or_create(
                            division=division,
                            codigo=centro_codigo,
                            defaults={'nombre': centro_nombre or centro_codigo},
                        )
                        if centro_nombre and centro_costo.nombre != centro_nombre:
                            centro_costo.nombre = centro_nombre
                            centro_costo.save(update_fields=['nombre'])

                        marca = _get_or_create_catalog(Marca, _get_row_value(row, 'Marca*'))
                        sistema_operativo = _get_or_create_catalog(
                            SistemaOperativo,
                            _get_row_value(row, 'Sistema operativo*'),
                        )
                        tipo_equipo = _get_or_create_catalog(TipoEquipo, _get_row_value(row, 'Tipo de equipos*'))
                        modelo = _get_or_create_catalog(ModeloEquipo, _get_row_value(row, 'Modelo*'))
                        codigo_postal = _normalize_value(
                            _get_row_value_by_headers(row, ['Código Postal', 'Codigo Postal'])
                        )
                        domicilio = _normalize_value(
                            _get_row_value_by_headers(row, ['Domicilio*', 'Domicilio'])
                        )
                        antiguedad = _normalize_value(
                            _get_row_value_by_headers(row, ['Antigüedad*', 'Antiguedad'])
                        )
                        rpe_responsable = _normalize_value(
                            _get_row_value_by_headers(row, ['RPE de Responsable'])
                        )
                        nombre_responsable = _normalize_value(
                            _get_row_value_by_headers(row, ['Nombre de Responsable'])
                        )
                        infraestructura_critica = _parse_boolean(
                            _get_row_value_by_headers(row, ['Es infraestructura crítica?', 'Es infraestructura critica?'])
                        )

                        equipo_existente = Equipo.objects.filter(identificador=identificador).first()
                        if equipo_existente and modo == 'create_only':
                            resultados['omitidos'] += 1
                            continue
                        if not equipo_existente and modo == 'update_only':
                            resultados['omitidos'] += 1
                            continue

                        defaults = {
                            'centro_costo': centro_costo,
                            'clave': clave,
                            'numero_inventario': inventario,
                            'nombre': nombre_equipo,
                            'numero_serie': numero_serie,
                            'marca': marca,
                            'sistema_operativo': sistema_operativo,
                            'tipo_equipo': tipo_equipo,
                            'modelo': modelo,
                            'codigo_postal': codigo_postal or None,
                            'domicilio': domicilio or None,
                            'antiguedad': antiguedad or None,
                            'rpe_responsable': rpe_responsable or None,
                            'nombre_responsable': nombre_responsable or None,
                            'infraestructura_critica': infraestructura_critica,
                        }
                        if equipo_existente:
                            for campo, valor in defaults.items():
                                setattr(equipo_existente, campo, valor)
                            equipo_existente.save()
                            resultados['actualizados'] += 1
                        else:
                            Equipo.objects.create(identificador=identificador, **defaults)
                            resultados['creados'] += 1
                    except Exception as exc:
                        resultados['errores'] += 1
                        resultados['omitidos'] += 1
                        if len(errores) < ERRORS_LIMIT:
                            errores.append(
                                {
                                    'fila': numero_fila,
                                    'identificador': identificador if 'identificador' in locals() else '',
                                    'mensaje': str(exc),
                                }
                            )

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
