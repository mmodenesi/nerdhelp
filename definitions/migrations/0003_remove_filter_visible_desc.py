# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0002_auto_20151125_1034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filter',
            name='visible_desc',
        ),
    ]
