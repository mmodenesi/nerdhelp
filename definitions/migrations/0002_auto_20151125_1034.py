# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visible_name', models.CharField(max_length=100)),
                ('visible_desc', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100)),
                ('active', models.BooleanField()),
            ],
        ),
        migrations.AlterField(
            model_name='concept',
            name='concept_type',
            field=models.CharField(default=b'D', max_length=1, choices=[(b'T', b'Teorema'), (b'L', b'Lema'), (b'D', 'Definici\xf3n'), (b'E', b'Ejemplo'), (b'P', b'Problema')]),
        ),
    ]
