from .permissions import can_audit, can_baja, can_edit, can_import, can_view_report


def navigation_permissions(request):
    user = request.user
    return {
        "can_audit": can_audit(user),
        "can_baja": can_baja(user),
        "can_edit": can_edit(user),
        "can_import": can_import(user),
        "can_view_report": can_view_report(user),
    }
