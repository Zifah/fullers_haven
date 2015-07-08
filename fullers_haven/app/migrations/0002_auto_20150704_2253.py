# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bulkplanactivation',
            options={'get_latest_by': 'date_activated'},
        ),
        migrations.AlterModelOptions(
            name='itemcategory',
            options={'verbose_name_plural': 'Item Categories'},
        ),
        migrations.RenameField(
            model_name='order',
            old_name='date_collected',
            new_name='date_delivered',
        ),
    ]
