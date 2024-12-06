# Generated by Django 5.1.2 on 2024-11-25 08:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppCodingNexus', '0013_classroom'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='AppCodingNexus.courses'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='classroom',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
