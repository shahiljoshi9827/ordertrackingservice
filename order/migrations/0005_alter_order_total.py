# Generated by Django 4.1 on 2022-08-21 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_alter_order_status_alter_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
