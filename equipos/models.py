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


class Equipo(models.Model):
    centro_costo = models.ForeignKey(
        CentroCosto,
        on_delete=models.PROTECT,
        related_name='equipos',
    )
    nombre = models.CharField(max_length=150)
    numero_serie = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.numero_serie})"
