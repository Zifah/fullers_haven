# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20150704_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkplanactivation',
            name='date_activated',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
