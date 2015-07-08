# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20150705_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkplan',
            name='number_of_items',
            field=models.PositiveSmallIntegerField(verbose_name=b'Total pieces'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.ForeignKey(related_name='items', blank=True, to='app.ItemCategory', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='code',
            field=models.CharField(max_length=3, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='code',
            field=models.CharField(max_length=3, null=True, blank=True),
            preserve_default=True,
        ),
    ]
