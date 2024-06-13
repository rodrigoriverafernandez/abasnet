# Generated by Django 3.2.7 on 2024-06-04 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0005_auto_20240603_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='Noticia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('contenido', models.TextField()),
                ('fecha_publicacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
