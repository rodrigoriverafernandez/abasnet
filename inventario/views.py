import csv
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

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


ALLOWED_GROUPS = {'ADMIN', 'SOPORTE'}
ERRORS_LIMIT = 50


def _user_can_import(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ALLOWED_GROUPS).exists()


def _normalize_value(value):
    if value is None:
        return ''
    cleaned = str(value).strip()
    if cleaned.lower() in {'no disponible', 'no aplica', 'n/a', 'na'}:
        return ''
    return cleaned


def _get_row_value(row, *keys):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return ''


def _get_or_create_catalog(model, value):
    cleaned = _normalize_value(value)
    if not cleaned:
        return None
    obj, _ = model.objects.get_or_create(nombre=cleaned)
    return obj


def permission_denied(request, exception=None):
    return render(request, '403.html', status=403)


@login_required
def importar_inventario(request):
    if not _user_can_import(request.user):
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
                        inventario = _normalize_value(_get_row_value(row, 'Número de inventario*'))
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
