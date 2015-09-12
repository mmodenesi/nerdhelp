# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('definition', models.TextField()),
                ('learning_coeff', models.FloatField(default=0.0, editable=False)),
                ('concept_type', models.CharField(default=b'D', max_length=1, choices=[(b'T', b'Teorema'), (b'L', b'Lema'), (b'D', b'Definici\xc3\xb3n'), (b'E', b'Ejemplo'), (b'P', b'Problema')])),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('card', models.ForeignKey(related_name='reactions', to='definitions.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
            ],
        ),
        migrations.AddField(
            model_name='concept',
            name='course',
            field=models.ForeignKey(to='definitions.Course'),
        ),
        migrations.AddField(
            model_name='concept',
            name='tags',
            field=models.ManyToManyField(to='definitions.Tag'),
        ),
    ]
