from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("equipos", "0005_auditlog_equipo"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipo",
            name="infraestructura_critica",
            field=models.BooleanField(default=False),
        ),
    ]
