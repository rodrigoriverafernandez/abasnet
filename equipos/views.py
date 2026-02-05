import csv
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.utils import timezone

from .models import AuditLog, BajaEquipo, Equipo


ALLOWED_BAJA_GROUPS = {"ADMIN", "SOPORTE"}
ALLOWED_REPORT_GROUPS = {"ADMIN", "SOPORTE"}
ALLOWED_REPORT_READONLY_GROUPS = {"CONSULTA"}


def _user_can_baja(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ALLOWED_BAJA_GROUPS).exists()


def _user_can_report(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ALLOWED_REPORT_GROUPS).exists()


def _user_can_view_report(user):
    if _user_can_report(user):
        return True
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=ALLOWED_REPORT_READONLY_GROUPS).exists()


def _build_querystring(request, exclude=None, extra=None):
    params = request.GET.copy()
    if exclude:
        for key in exclude:
            params.pop(key, None)
    if extra:
        for key, value in extra.items():
            params[key] = value
    return params.urlencode()


@login_required
def equipos_list(request):
    include_bajas = request.GET.get("include_bajas") == "1"
    codigo_postal = request.GET.get("codigo_postal", "").strip()
    rpe_responsable = request.GET.get("rpe_responsable", "").strip()
    nombre_responsable = request.GET.get("nombre_responsable", "").strip()
    equipos = (
        Equipo.objects.select_related(
            "centro_costo__division__sociedad",
            "marca",
            "sistema_operativo",
            "tipo_equipo",
            "modelo",
        )
        .order_by("identificador")
    )
    if not include_bajas:
        equipos = equipos.filter(is_baja=False)
    if codigo_postal:
        equipos = equipos.filter(codigo_postal__icontains=codigo_postal)
    if rpe_responsable:
        equipos = equipos.filter(rpe_responsable__icontains=rpe_responsable)
    if nombre_responsable:
        equipos = equipos.filter(nombre_responsable__icontains=nombre_responsable)

    context = {
        "equipos": equipos,
        "include_bajas": include_bajas,
        "filtros": {
            "codigo_postal": codigo_postal,
            "rpe_responsable": rpe_responsable,
            "nombre_responsable": nombre_responsable,
        },
        "can_baja": _user_can_baja(request.user),
    }
    return render(request, "equipos/list.html", context)


@login_required
def equipo_detail(request, pk):
    equipo = get_object_or_404(
        Equipo.objects.select_related(
            "centro_costo__division__sociedad",
            "marca",
            "sistema_operativo",
            "tipo_equipo",
            "modelo",
        ),
        pk=pk,
    )
    context = {
        "equipo": equipo,
        "can_baja": _user_can_baja(request.user),
    }
    return render(request, "equipos/detail.html", context)


@login_required
def equipo_baja(request, pk):
    if not _user_can_baja(request.user):
        return render(request, "403.html", status=403)

    equipo = get_object_or_404(Equipo, pk=pk)
    if equipo.is_baja:
        messages.warning(request, "El equipo ya se encuentra dado de baja.")
        return redirect("equipo_detail", pk=equipo.pk)

    if request.method == "POST":
        tipo_baja = request.POST.get("tipo_baja")
        valid_choices = {choice[0] for choice in BajaEquipo.TipoBaja.choices}
        if tipo_baja not in valid_choices:
            messages.error(request, "Seleccione un tipo de baja válido.")
        else:
            equipo.is_baja = True
            equipo.fecha_baja = timezone.now()
            equipo.save(update_fields=["is_baja", "fecha_baja"])
            BajaEquipo.objects.create(
                equipo=equipo,
                fecha_baja=equipo.fecha_baja,
                tipo_baja=tipo_baja,
            )
            AuditLog.objects.create(
                usuario=request.user,
                accion="BAJA",
                resumen=(
                    f"Baja registrada para el equipo {equipo.identificador} "
                    f"({equipo.numero_serie})."
                ),
            )
            messages.success(request, "La baja se registró correctamente.")
            return redirect("equipo_detail", pk=equipo.pk)

    context = {
        "equipo": equipo,
        "tipos_baja": BajaEquipo.TipoBaja.choices,
    }
    return render(request, "equipos/baja_form.html", context)


@login_required
def bajas_list(request):
    if not _user_can_baja(request.user):
        return render(request, "403.html", status=403)

    bajas = (
        BajaEquipo.objects.select_related("equipo")
        .order_by("-fecha_baja")
    )
    context = {
        "bajas": bajas,
    }
    return render(request, "bajas/list.html", context)


@login_required
def reportes_home(request):
    if not _user_can_view_report(request.user):
        return render(request, "403.html", status=403)

    context = {
        "can_export": _user_can_report(request.user),
    }
    return render(request, "reportes/index.html", context)


@login_required
def reporte_inventario_activo(request):
    if not _user_can_view_report(request.user):
        return render(request, "403.html", status=403)

    equipos = (
        Equipo.objects.select_related(
            "centro_costo__division__sociedad",
            "marca",
            "sistema_operativo",
            "tipo_equipo",
            "modelo",
        )
        .filter(activo=True, is_baja=False)
        .order_by("identificador")
    )

    sociedad_id = request.GET.get("sociedad")
    division_id = request.GET.get("division")
    centro_costo_id = request.GET.get("centro_costo")
    marca_id = request.GET.get("marca")
    sistema_operativo_id = request.GET.get("sistema_operativo")
    tipo_equipo_id = request.GET.get("tipo_equipo")
    texto = request.GET.get("texto")

    if sociedad_id:
        equipos = equipos.filter(centro_costo__division__sociedad_id=sociedad_id)
    if division_id:
        equipos = equipos.filter(centro_costo__division_id=division_id)
    if centro_costo_id:
        equipos = equipos.filter(centro_costo_id=centro_costo_id)
    if marca_id:
        equipos = equipos.filter(marca_id=marca_id)
    if sistema_operativo_id:
        equipos = equipos.filter(sistema_operativo_id=sistema_operativo_id)
    if tipo_equipo_id:
        equipos = equipos.filter(tipo_equipo_id=tipo_equipo_id)
    if texto:
        equipos = equipos.filter(
            Q(identificador__icontains=texto)
            | Q(numero_inventario__icontains=texto)
            | Q(numero_serie__icontains=texto)
            | Q(nombre__icontains=texto)
        )

    if request.GET.get("export") == "1":
        if not _user_can_report(request.user):
            return render(request, "403.html", status=403)
        return _export_inventario_activo_csv(equipos)

    paginator = Paginator(equipos, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "sociedades": Equipo.objects.values_list(
            "centro_costo__division__sociedad__id",
            "centro_costo__division__sociedad__codigo",
            "centro_costo__division__sociedad__nombre",
        )
        .distinct()
        .order_by("centro_costo__division__sociedad__codigo"),
        "divisiones": Equipo.objects.values_list(
            "centro_costo__division__id",
            "centro_costo__division__codigo",
            "centro_costo__division__nombre",
        )
        .distinct()
        .order_by("centro_costo__division__codigo"),
        "centros_costo": Equipo.objects.values_list(
            "centro_costo__id",
            "centro_costo__codigo",
            "centro_costo__nombre",
        )
        .distinct()
        .order_by("centro_costo__codigo"),
        "marcas": Equipo.objects.values_list("marca__id", "marca__nombre")
        .distinct()
        .order_by("marca__nombre"),
        "sistemas_operativos": Equipo.objects.values_list(
            "sistema_operativo__id",
            "sistema_operativo__nombre",
        )
        .distinct()
        .order_by("sistema_operativo__nombre"),
        "tipos_equipo": Equipo.objects.values_list("tipo_equipo__id", "tipo_equipo__nombre")
        .distinct()
        .order_by("tipo_equipo__nombre"),
        "filtros": {
            "sociedad": sociedad_id or "",
            "division": division_id or "",
            "centro_costo": centro_costo_id or "",
            "marca": marca_id or "",
            "sistema_operativo": sistema_operativo_id or "",
            "tipo_equipo": tipo_equipo_id or "",
            "texto": texto or "",
        },
        "pagination_query": _build_querystring(request, exclude={"page"}),
        "export_query": _build_querystring(request, exclude={"page"}, extra={"export": "1"}),
        "can_export": _user_can_report(request.user),
    }
    return render(request, "reportes/inventario_activo.html", context)


@login_required
def reporte_equipos_baja(request):
    if not _user_can_view_report(request.user):
        return render(request, "403.html", status=403)

    bajas_queryset = BajaEquipo.objects.order_by("-fecha_baja")
    equipos = (
        Equipo.objects.select_related(
            "centro_costo__division__sociedad",
            "marca",
            "tipo_equipo",
        )
        .prefetch_related(Prefetch("bajas", queryset=bajas_queryset))
        .filter(is_baja=True)
        .order_by("-fecha_baja", "identificador")
    )

    fecha_desde = parse_date(request.GET.get("fecha_desde") or "")
    fecha_hasta = parse_date(request.GET.get("fecha_hasta") or "")
    motivo = request.GET.get("motivo")

    if fecha_desde:
        equipos = equipos.filter(fecha_baja__date__gte=fecha_desde)
    if fecha_hasta:
        equipos = equipos.filter(fecha_baja__date__lte=fecha_hasta)
    if motivo:
        equipos = equipos.filter(bajas__tipo_baja=motivo)

    equipos = equipos.distinct()

    if request.GET.get("export") == "1":
        if not _user_can_report(request.user):
            return render(request, "403.html", status=403)
        return _export_equipos_baja_csv(equipos)

    context = {
        "equipos": equipos,
        "filtros": {
            "fecha_desde": request.GET.get("fecha_desde") or "",
            "fecha_hasta": request.GET.get("fecha_hasta") or "",
            "motivo": motivo or "",
        },
        "tipos_baja": BajaEquipo.TipoBaja.choices,
        "export_query": _build_querystring(request, extra={"export": "1"}),
        "can_export": _user_can_report(request.user),
    }
    return render(request, "reportes/equipos_baja.html", context)


@login_required
def reporte_resumen(request):
    if not _user_can_view_report(request.user):
        return render(request, "403.html", status=403)

    activos = Equipo.objects.filter(activo=True, is_baja=False)
    bajas = Equipo.objects.filter(is_baja=True)

    resumen_sociedad = (
        activos.values(
            "centro_costo__division__sociedad__codigo",
            "centro_costo__division__sociedad__nombre",
        )
        .annotate(total=Count("id"))
        .order_by("centro_costo__division__sociedad__codigo")
    )
    resumen_tipo = (
        activos.values("tipo_equipo__nombre")
        .annotate(total=Count("id"))
        .order_by("tipo_equipo__nombre")
    )
    resumen_bajas = (
        BajaEquipo.objects.values("tipo_baja")
        .annotate(total=Count("id"))
        .order_by("tipo_baja")
    )
    motivo_lookup = dict(BajaEquipo.TipoBaja.choices)
    resumen_bajas = [
        {
            "tipo_baja": fila["tipo_baja"],
            "tipo_baja_display": motivo_lookup.get(fila["tipo_baja"], fila["tipo_baja"]),
            "total": fila["total"],
        }
        for fila in resumen_bajas
    ]

    context = {
        "total_equipos": Equipo.objects.count(),
        "total_activos": activos.count(),
        "total_bajas": bajas.count(),
        "resumen_sociedad": resumen_sociedad,
        "resumen_tipo": resumen_tipo,
        "resumen_bajas": resumen_bajas,
    }
    return render(request, "reportes/resumen.html", context)


def _export_inventario_activo_csv(equipos):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="reporte_inventario_activo.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Identificador",
            "Inventario",
            "Serie",
            "Nombre",
            "Sociedad",
            "Division",
            "Centro de costo",
            "Marca",
            "Sistema operativo",
            "Tipo equipo",
            "Modelo",
        ]
    )
    for equipo in equipos:
        writer.writerow(
            [
                equipo.identificador,
                equipo.numero_inventario,
                equipo.numero_serie,
                equipo.nombre,
                equipo.centro_costo.division.sociedad,
                equipo.centro_costo.division,
                equipo.centro_costo,
                equipo.marca or "",
                equipo.sistema_operativo or "",
                equipo.tipo_equipo or "",
                equipo.modelo or "",
            ]
        )
    return response


def _export_equipos_baja_csv(equipos):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="reporte_equipos_baja.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Identificador",
            "Inventario",
            "Serie",
            "Nombre",
            "Fecha baja",
            "Motivo",
            "Sociedad",
            "Division",
            "Centro de costo",
            "Marca",
            "Tipo equipo",
        ]
    )
    for equipo in equipos:
        baja = equipo.bajas.all().first()
        writer.writerow(
            [
                equipo.identificador,
                equipo.numero_inventario,
                equipo.numero_serie,
                equipo.nombre,
                equipo.fecha_baja.strftime("%Y-%m-%d %H:%M") if equipo.fecha_baja else "",
                baja.get_tipo_baja_display() if baja else "",
                equipo.centro_costo.division.sociedad,
                equipo.centro_costo.division,
                equipo.centro_costo,
                equipo.marca or "",
                equipo.tipo_equipo or "",
            ]
        )
    return response
