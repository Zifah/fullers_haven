# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20150705_2204'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveSmallIntegerField()),
                ('item', models.ForeignKey(to='app.Item')),
                ('product', models.ForeignKey(related_name='items', to='app.Product')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='product',
            name='items',
        ),
    ]
