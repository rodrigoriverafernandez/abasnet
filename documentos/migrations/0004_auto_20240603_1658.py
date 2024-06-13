# Generated by Django 3.2.7 on 2024-06-03 22:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('documentos', '0003_alter_anuncio_importancia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anuncio',
            name='autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
        ),
        migrations.AlterField(
            model_name='anuncio',
            name='importancia',
            field=models.CharField(choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')], max_length=50),
        ),
    ]
