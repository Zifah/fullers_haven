# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20150705_2150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='code',
        ),
        migrations.RemoveField(
            model_name='product',
            name='code',
        ),
    ]
