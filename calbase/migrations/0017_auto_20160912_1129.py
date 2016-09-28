# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-12 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calbase', '0016_auto_20160909_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='calibration',
            name='cal_17025_check',
            field=models.CharField(choices=[('Yes', 'Yes'), ('Wavier List', 'Wavier List')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='calibration',
            name='location',
            field=models.CharField(choices=[('Cali', 'Cali'), ('MD', 'MD'), ('Out', 'Out')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='calibration',
            name='qc_test_by',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='calibration',
            name='qc_test_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='cal_cert_location',
            field=models.FilePathField(match='.*\\.(pdf)$', max_length=300, null=True, path='H:\\Internal PCTEST Applications\\intranet\\LAB (testing)\\Cal'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='cal_due_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='department',
            field=models.CharField(blank=True, choices=[('Battery', 'Battery'), ('EMC', 'EMC'), ('SAR/HAC', 'SAR/HAC'), ('Wireless', 'Wireless')], max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='is_flagged',
            field=models.CharField(blank=True, default='', editable=False, max_length=100),
        ),
        migrations.AddField(
            model_name='equipment',
            name='manual_location',
            field=models.FilePathField(match='.*\\.(pdf)$', max_length=300, null=True, path='H:\\Internal PCTEST Applications\\intranet\\LAB (testing)\\Cal'),
        ),
    ]
