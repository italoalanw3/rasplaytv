# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-14 23:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playtv', '0005_auto_20160214_2309'),
    ]

    operations = [
        migrations.AddField(
            model_name='linksepisodioseriado',
            name='execucao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='playtv.Execucao'),
        ),
        migrations.AddField(
            model_name='linksfilme',
            name='execucao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='playtv.Execucao'),
        ),
    ]
