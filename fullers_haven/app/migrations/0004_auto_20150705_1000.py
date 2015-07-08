# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20150704_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkplanactivation',
            name='month',
            field=models.PositiveSmallIntegerField(max_length=1, choices=[(1, b'January'), (2, b'February'), (3, b'March'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bulkplanpayment',
            name='month',
            field=models.PositiveSmallIntegerField(max_length=1, choices=[(1, b'January'), (2, b'February'), (3, b'March'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')]),
            preserve_default=True,
        ),
    ]
