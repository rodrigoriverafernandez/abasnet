from django.db import models
from django.utils import timezone


class Sociedad(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Division(models.Model):
    sociedad = models.ForeignKey(Sociedad, on_delete=models.PROTECT, related_name='divisiones')
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50)

    class Meta:
        unique_together = ('sociedad', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CentroCosto(models.Model):
    division = models.ForeignKey(Division, on_delete=models.PROTECT, related_name='centros_costo')
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50)

    class Meta:
        unique_together = ('division', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Marca(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre


class SistemaOperativo(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre


class TipoEquipo(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre


class ModeloEquipo(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    centro_costo = models.ForeignKey(
        CentroCosto,
        on_delete=models.PROTECT,
        related_name='equipos',
    )
    identificador = models.CharField(max_length=150, unique=True)
    clave = models.CharField(max_length=150, blank=True)
    numero_inventario = models.CharField(max_length=150, blank=True)
    nombre = models.CharField(max_length=150)
    numero_serie = models.CharField(max_length=100, unique=True)
    direccion_ip = models.CharField(max_length=50, blank=True, null=True)
    direccion_mac = models.CharField(max_length=50, blank=True, null=True)
    entidad = models.CharField(max_length=150, blank=True, null=True)
    municipio = models.CharField(max_length=150, blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, null=True, blank=True)
    sistema_operativo = models.ForeignKey(
        SistemaOperativo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.PROTECT, null=True, blank=True)
    modelo = models.ForeignKey(ModeloEquipo, on_delete=models.PROTECT, null=True, blank=True)
    activo = models.BooleanField(default=True)
    is_baja = models.BooleanField(default=False)
    fecha_baja = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    domicilio = models.CharField(max_length=255, blank=True, null=True)
    antiguedad = models.CharField(max_length=50, blank=True, null=True)
    rpe_responsable = models.CharField(max_length=15, blank=True, null=True)
    nombre_responsable = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.numero_serie})"

    def registrar_baja(self, tipo_baja, usuario=None, resumen=None, motivo=None, comentarios=None):
        self.is_baja = True
        self.fecha_baja = timezone.now()
        update_fields = ["is_baja", "fecha_baja"]
        if hasattr(self, "estado"):
            try:
                self.estado = "BAJA"
                update_fields.append("estado")
            except (TypeError, ValueError):
                pass
        self.save(update_fields=update_fields)
        BajaEquipo.objects.create(
            equipo=self,
            fecha_baja=self.fecha_baja,
            tipo_baja=tipo_baja,
            motivo=motivo,
            comentarios=comentarios or "",
            usuario=usuario,
        )
        if resumen is None:
            resumen = f"Baja registrada para el equipo {self.identificador} ({self.numero_serie})."
        AuditLog.objects.create(
            usuario=usuario,
            accion="BAJA_EQUIPO",
            resumen=resumen,
        )


class ImportLog(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    archivo = models.CharField(max_length=255)
    total_filas = models.PositiveIntegerField(default=0)
    creados = models.PositiveIntegerField(default=0)
    actualizados = models.PositiveIntegerField(default=0)
    omitidos = models.PositiveIntegerField(default=0)
    errores = models.PositiveIntegerField(default=0)
    resumen_errores = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Importación {self.fecha:%Y-%m-%d %H:%M}"


class AuditLog(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=50)
    resumen = models.TextField()

    def __str__(self):
        return f"{self.accion} {self.fecha:%Y-%m-%d %H:%M}"


class MotivoBaja(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre


class BajaEquipo(models.Model):
    class TipoBaja(models.TextChoices):
        TEMPORAL = "TEMPORAL", "Temporal"
        DEFINITIVA = "DEFINITIVA", "Definitiva"

    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name="bajas")
    fecha_baja = models.DateTimeField(default=timezone.now)
    tipo_baja = models.CharField(max_length=20, choices=TipoBaja.choices)
    motivo = models.ForeignKey(
        MotivoBaja,
        on_delete=models.PROTECT,
        related_name="bajas",
        null=True,
        blank=True,
    )
    comentarios = models.TextField(blank=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.equipo.identificador} - {self.get_tipo_baja_display()}"
