# Generated by Django 5.0 on 2025-05-10 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='grado',
            field=models.IntegerField(default=0),
        ),
    ]
