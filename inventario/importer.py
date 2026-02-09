import csv
import re
import unicodedata

from equipos.models import (
    CentroCosto,
    Division,
    Equipo,
    Marca,
    ModeloEquipo,
    SistemaOperativo,
    Sociedad,
    TipoEquipo,
)

ERRORS_LIMIT = 50


def normalize_value(value):
    if value is None:
        return ""
    cleaned = unicodedata.normalize("NFKC", str(value)).strip()
    if cleaned.lower() in {"no disponible", "no aplica", "n/a", "na"}:
        return ""
    return cleaned


def normalize_header(value):
    if value is None:
        return ""
    cleaned = str(value).lstrip("\ufeff").strip()
    cleaned = re.sub(r"[:*]+$", "", cleaned)
    cleaned = " ".join(cleaned.split())
    cleaned = cleaned.lower()
    cleaned = unicodedata.normalize("NFD", cleaned)
    return "".join(char for char in cleaned if not unicodedata.combining(char))


def build_normalized_row(row):
    return {normalize_header(key): value for key, value in row.items()}


def get_row_value(row, normalized_row, *headers):
    for header in headers:
        normalized_header = normalize_header(header)
        if normalized_header in normalized_row and normalized_row[normalized_header] is not None:
            return normalized_row[normalized_header]
    return ""


def get_or_create_catalog(model, value):
    cleaned = normalize_value(value)
    if not cleaned:
        return None
    obj, _ = model.objects.get_or_create(nombre=cleaned)
    return obj


def parse_boolean(value):
    cleaned = normalize_value(value)
    if not cleaned:
        return False
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", cleaned)
        if not unicodedata.combining(char)
    ).lower()
    return normalized in {"si", "sí", "s", "true", "1", "x", "yes"}


def import_inventario_csv(path, modo):
    resultados = {
        "total": 0,
        "creados": 0,
        "actualizados": 0,
        "omitidos": 0,
        "errores": 0,
    }
    errores = []

    if not path.exists():
        errores.append({"fila": "-", "identificador": "-", "mensaje": "No se encontró el archivo CSV."})
        resultados["errores"] = 1
        resultados["omitidos"] = 1
        return resultados, errores

    with open(path, encoding="utf-8", errors="replace", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for numero_fila, row in enumerate(lector, start=2):
            resultados["total"] += 1
            identificador = ""
            try:
                normalized_row = build_normalized_row(row)
                inventario = normalize_value(
                    get_row_value(
                        row,
                        normalized_row,
                        "Número de inventario",
                        "Numero de inventario",
                        "No. de inventario",
                        "Inventario",
                    )
                )
                numero_serie = normalize_value(
                    get_row_value(
                        row,
                        normalized_row,
                        "Número de serie",
                        "Numero de serie",
                        "No. de serie",
                        "Serie",
                    )
                )
                clave = normalize_value(get_row_value(row, normalized_row, "Clave"))
                identificador = inventario or clave or numero_serie
                if not identificador:
                    raise ValueError("Identificador vacío (Número de inventario, Clave o Número de serie).")

                if not numero_serie:
                    raise ValueError("Número de serie vacío.")

                nombre_equipo = normalize_value(get_row_value(row, normalized_row, "Nombre")) or identificador

                sociedad_codigo = normalize_value(get_row_value(row, normalized_row, "Sociedad"))
                sociedad_nombre = (
                    normalize_value(get_row_value(row, normalized_row, "Nombre de Sociedad"))
                    or sociedad_codigo
                )
                if not sociedad_codigo:
                    raise ValueError("Sociedad vacía.")
                sociedad, _ = Sociedad.objects.get_or_create(
                    codigo=sociedad_codigo,
                    defaults={"nombre": sociedad_nombre or sociedad_codigo},
                )
                if sociedad_nombre and sociedad.nombre != sociedad_nombre:
                    sociedad.nombre = sociedad_nombre
                    sociedad.save(update_fields=["nombre"])

                division_codigo = normalize_value(get_row_value(row, normalized_row, "División", "Division"))
                division_nombre = (
                    normalize_value(get_row_value(row, normalized_row, "Nombre de División", "Nombre de Division"))
                    or division_codigo
                )
                if not division_codigo:
                    raise ValueError("División vacía.")
                division, _ = Division.objects.get_or_create(
                    sociedad=sociedad,
                    codigo=division_codigo,
                    defaults={"nombre": division_nombre or division_codigo},
                )
                if division_nombre and division.nombre != division_nombre:
                    division.nombre = division_nombre
                    division.save(update_fields=["nombre"])

                centro_codigo = normalize_value(
                    get_row_value(row, normalized_row, "Centro de Costo", "Centro de costo")
                )
                centro_nombre = centro_codigo
                if not centro_codigo:
                    raise ValueError("Centro de costo vacío.")
                centro_costo, _ = CentroCosto.objects.get_or_create(
                    division=division,
                    codigo=centro_codigo,
                    defaults={"nombre": centro_nombre or centro_codigo},
                )
                if centro_nombre and centro_costo.nombre != centro_nombre:
                    centro_costo.nombre = centro_nombre
                    centro_costo.save(update_fields=["nombre"])

                marca = get_or_create_catalog(Marca, get_row_value(row, normalized_row, "Marca"))
                sistema_operativo = get_or_create_catalog(
                    SistemaOperativo, get_row_value(row, normalized_row, "Sistema operativo")
                )
                tipo_equipo = get_or_create_catalog(
                    TipoEquipo,
                    get_row_value(row, normalized_row, "Tipo de equipos", "Tipo de equipo"),
                )
                modelo = get_or_create_catalog(ModeloEquipo, get_row_value(row, normalized_row, "Modelo"))
                codigo_postal = normalize_value(
                    get_row_value(row, normalized_row, "Código Postal", "Codigo Postal")
                )
                domicilio = normalize_value(get_row_value(row, normalized_row, "Domicilio"))
                antiguedad = normalize_value(
                    get_row_value(row, normalized_row, "Antigüedad", "Antiguedad")
                )
                rpe_responsable = normalize_value(
                    get_row_value(row, normalized_row, "RPE de Responsable")
                )
                nombre_responsable = normalize_value(
                    get_row_value(row, normalized_row, "Nombre de Responsable")
                )
                infraestructura_critica = parse_boolean(
                    get_row_value(
                        row,
                        normalized_row,
                        "Es infraestructura crítica?",
                        "Es infraestructura critica?",
                    )
                )
                direccion_ip = normalize_value(
                    get_row_value(row, normalized_row, "Dirección IP", "Direccion IP", "IP")
                )
                direccion_mac = normalize_value(
                    get_row_value(row, normalized_row, "Dirección MAC", "Direccion MAC", "MAC")
                )
                entidad = normalize_value(get_row_value(row, normalized_row, "Entidad"))
                municipio = normalize_value(get_row_value(row, normalized_row, "Municipio"))

                equipo_existente = Equipo.objects.filter(numero_serie=numero_serie).first()
                if equipo_existente and modo == "create_only":
                    resultados["omitidos"] += 1
                    continue
                if not equipo_existente and modo == "update_only":
                    resultados["omitidos"] += 1
                    continue

                def inventario_duplicado():
                    if not inventario:
                        return False
                    qs = Equipo.objects.filter(numero_inventario=inventario)
                    if equipo_existente:
                        qs = qs.exclude(pk=equipo_existente.pk)
                    return qs.exists()

                should_update_inventario = False
                if inventario:
                    if equipo_existente:
                        if not equipo_existente.numero_inventario:
                            if inventario_duplicado():
                                raise ValueError("Número de inventario ya existe en otro equipo.")
                            should_update_inventario = True
                        elif equipo_existente.numero_inventario != inventario:
                            if inventario_duplicado():
                                raise ValueError("Número de inventario ya existe en otro equipo.")
                            should_update_inventario = True
                    else:
                        if inventario_duplicado():
                            raise ValueError("Número de inventario ya existe en otro equipo.")

                numero_inventario_value = inventario
                if equipo_existente and not should_update_inventario:
                    numero_inventario_value = equipo_existente.numero_inventario

                defaults = {
                    "centro_costo": centro_costo,
                    "clave": clave,
                    "numero_inventario": numero_inventario_value,
                    "nombre": nombre_equipo,
                    "numero_serie": numero_serie,
                    "marca": marca,
                    "sistema_operativo": sistema_operativo,
                    "tipo_equipo": tipo_equipo,
                    "modelo": modelo,
                    "codigo_postal": codigo_postal or None,
                    "domicilio": domicilio or None,
                    "antiguedad": antiguedad or None,
                    "rpe_responsable": rpe_responsable or None,
                    "nombre_responsable": nombre_responsable or None,
                    "infraestructura_critica": infraestructura_critica,
                    "direccion_ip": direccion_ip or None,
                    "direccion_mac": direccion_mac or None,
                    "entidad": entidad or None,
                    "municipio": municipio or None,
                }

                if equipo_existente:
                    for campo, valor in defaults.items():
                        setattr(equipo_existente, campo, valor)
                    equipo_existente.save()
                    resultados["actualizados"] += 1
                else:
                    Equipo.objects.create(identificador=identificador, **defaults)
                    resultados["creados"] += 1
            except Exception as exc:
                resultados["errores"] += 1
                resultados["omitidos"] += 1
                if len(errores) < ERRORS_LIMIT:
                    errores.append(
                        {
                            "fila": numero_fila,
                            "identificador": identificador,
                            "mensaje": str(exc),
                        }
                    )

    return resultados, errores
