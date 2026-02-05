from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import AuditLog, BajaEquipo, Equipo


ALLOWED_BAJA_GROUPS = {"ADMIN", "SOPORTE"}


def _user_can_baja(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ALLOWED_BAJA_GROUPS).exists()


@login_required
def equipos_list(request):
    include_bajas = request.GET.get("include_bajas") == "1"
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

    context = {
        "equipos": equipos,
        "include_bajas": include_bajas,
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
