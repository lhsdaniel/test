# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-20 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calbase', '0021_auto_20160920_1531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipment',
            name='cal_cert_location',
        ),
        migrations.AddField(
            model_name='calibration',
            name='cal_cert_location',
            field=models.FileField(blank=True, null=True, upload_to='cal_cert/'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='manual_location',
            field=models.FileField(blank=True, null=True, upload_to='manual/'),
        ),
    ]
