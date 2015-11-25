# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0003_remove_filter_visible_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filter',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
