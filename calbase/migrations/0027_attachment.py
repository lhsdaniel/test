# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 20:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calbase', '0026_auto_20160923_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(blank=True, null=True, upload_to='picture/%Y/%m/%d')),
                ('equip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calbase.Equipment')),
            ],
        ),
    ]
