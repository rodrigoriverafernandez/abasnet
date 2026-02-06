from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("equipos", "0004_motivobaja_bajaequipo_comentarios_bajaequipo_usuario_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="auditlog",
            name="equipo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="audit_logs",
                to="equipos.equipo",
            ),
        ),
    ]
