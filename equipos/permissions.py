ALLOWED_BAJA_GROUPS = {"ADMIN", "SOPORTE"}
ALLOWED_REPORT_GROUPS = {"ADMIN", "SOPORTE"}
ALLOWED_REPORT_READONLY_GROUPS = {"CONSULTA"}


def _user_in_groups(user, groups):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=groups).exists()


def can_baja(user):
    return _user_in_groups(user, ALLOWED_BAJA_GROUPS)


def can_edit(user):
    return _user_in_groups(user, ALLOWED_BAJA_GROUPS)


def can_audit(user):
    return _user_in_groups(user, ALLOWED_BAJA_GROUPS)


def can_report(user):
    return _user_in_groups(user, ALLOWED_REPORT_GROUPS)


def can_view_report(user):
    if can_report(user):
        return True
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=ALLOWED_REPORT_READONLY_GROUPS).exists()


def can_import(user):
    return _user_in_groups(user, ALLOWED_BAJA_GROUPS)
