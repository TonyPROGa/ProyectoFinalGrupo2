# Generated by Django 3.2.2 on 2024-02-25 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0053_order_contenido'),
    ]

    operations = [
        migrations.AddField(
            model_name='aperturacaja',
            name='caja_num',
            field=models.CharField(choices=[('1', 'Número 1'), ('2', 'Número 2')], default=1, max_length=1),
        ),
    ]
