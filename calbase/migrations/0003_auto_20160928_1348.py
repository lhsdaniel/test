# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-28 17:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calbase', '0002_auto_20160928_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='equip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='calbase.Equipment'),
        ),
        migrations.AlterField(
            model_name='calibration',
            name='mesure_uncertainty_included',
            field=models.BooleanField(default=False, verbose_name='MU'),
        ),
    ]
