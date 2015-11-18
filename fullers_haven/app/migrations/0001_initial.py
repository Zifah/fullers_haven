# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alteration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=1, max_length=1, choices=[(0, b'Inactive'), (1, b'Active')])),
                ('name', models.CharField(unique=True, max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AppSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BulkPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=8, decimal_places=2)),
                ('number_of_items', models.PositiveSmallIntegerField(verbose_name=b'Total pieces')),
                ('number_of_months_valid', models.PositiveSmallIntegerField()),
                ('owner', models.OneToOneField(related_name='bulk_plan', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BulkPlanActivation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_activated', models.DateTimeField(auto_now_add=True)),
                ('month', models.PositiveSmallIntegerField(choices=[(1, b'January'), (2, b'February'), (3, b'March'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')])),
                ('activated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('bulk_plan', models.ForeignKey(related_name='activations', to='app.BulkPlan')),
            ],
            options={
                'get_latest_by': 'date_activated',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BulkPlanItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('max_quantity', models.PositiveSmallIntegerField(null=True, verbose_name=b'Max. quantity', blank=True)),
                ('bulk_plan', models.ForeignKey(related_name='items', to='app.BulkPlan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BulkPlanPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.PositiveSmallIntegerField(choices=[(1, b'January'), (2, b'February'), (3, b'March'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')])),
                ('bulk_plan', models.ForeignKey(to='app.BulkPlan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Colour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=1, max_length=1, choices=[(0, b'Inactive'), (1, b'Active')])),
                ('name', models.CharField(unique=True, max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=1, max_length=1, choices=[(0, b'Inactive'), (1, b'Active')])),
                ('name', models.CharField(unique=True, max_length=50)),
                ('percentage', models.DecimalField(max_digits=5, decimal_places=2)),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=1, max_length=1, choices=[(0, b'Inactive'), (1, b'Active')])),
                ('name', models.CharField(unique=True, max_length=50)),
                ('price', models.DecimalField(max_digits=8, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=1, max_length=1, choices=[(0, b'Inactive'), (1, b'Active')])),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Item Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.CharField(unique=True, max_length=20)),
                ('date_initiated', models.DateTimeField()),
                ('date_fulfillment_scheduled', models.DateField()),
                ('date_fulfillment_actual', models.DateField(null=True, blank=True)),
                ('date_delivered', models.DateField(null=True, blank=True)),
                ('type', models.CharField(max_length=1, choices=[(b'N', b'Normal'), (b'B', b'Bulk')])),
                ('amount', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('amount_discount', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('amount_payable', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'C', b'Cancelled'), (b'P', b'Processing'), (b'F', b'Fulfilled'), (b'D', b'Delivered')])),
                ('comments', models.TextField()),
                ('attendant_staff', models.ForeignKey(related_name='orders_received_by', to=settings.AUTH_USER_MODEL)),
                ('bulk_plan', models.ForeignKey(blank=True, to='app.BulkPlan', null=True)),
                ('customer', models.ForeignKey(related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('discount', models.ForeignKey(blank=True, to='app.Discount', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=1, choices=[(b'C', b'Creation'), (b'F', b'Fulfilment'), (b'X', b'Cancellation'), (b'D', b'Delivery/Pick-up')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('extra_information', models.TextField()),
                ('actor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(related_name='actions', to='app.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial_number', models.PositiveSmallIntegerField(default=0)),
                ('item_name', models.CharField(max_length=50)),
                ('alteration_text', models.CharField(max_length=255, null=True, blank=True)),
                ('item_tag', models.CharField(unique=True, max_length=50)),
                ('alteration', models.ForeignKey(blank=True, to='app.Alteration', null=True)),
                ('colour', models.ForeignKey(to='app.Colour')),
                ('item', models.ForeignKey(to='app.Item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.ForeignKey(to='app.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial_number', models.PositiveSmallIntegerField(default=0)),
                ('product_name', models.CharField(max_length=50)),
                ('product_price', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('order', models.ForeignKey(related_name='order_products', to='app.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=1, max_length=1, choices=[(0, b'Inactive'), (1, b'Active')])),
                ('amount', models.DecimalField(default=0, max_digits=15, decimal_places=2)),
                ('payer', models.CharField(max_length=255, null=True, blank=True)),
                ('purpose', models.CharField(max_length=1, choices=[(b'B', b'Bulk plan'), (b'O', b'Order')])),
                ('instrument', models.CharField(max_length=1, choices=[(b'C', b'Cash'), (b'O', b'Electronic (Web, ATM, Transfer)'), (b'B', b'Bank (Teller)')])),
                ('reference', models.CharField(max_length=30, null=True, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('cashier', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(related_name='payments', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=1, max_length=1, choices=[(0, b'Inactive'), (1, b'Active')])),
                ('name', models.CharField(unique=True, max_length=50)),
                ('type', models.CharField(default=b'M', max_length=1, choices=[(b'A', b'Automatic'), (b'M', b'Manual')])),
                ('price', models.DecimalField(max_digits=8, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
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
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.CharField(max_length=20, null=True, blank=True)),
                ('home_address', models.CharField(max_length=255, null=True, blank=True)),
                ('work_address', models.CharField(max_length=255, null=True, blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='product',
            field=models.ForeignKey(to='app.Product'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='payment',
            field=models.OneToOneField(related_name='order_payment', to='app.Payment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order_product',
            field=models.ForeignKey(related_name='order_items', to='app.OrderProduct'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(related_name='items', to='app.ItemCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bulkplanpayment',
            name='payment',
            field=models.OneToOneField(related_name='bulk_plan_payment', to='app.Payment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bulkplanitem',
            name='product',
            field=models.ForeignKey(to='app.Product'),
            preserve_default=True,
        ),
    ]
