from django.db import models


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
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.numero_serie})"


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
