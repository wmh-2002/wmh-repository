# Generated by Django 5.0.7 on 2024-10-13 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_product_shopping_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.IntegerField(blank=True, default=1, null=True, verbose_name='库存数量'),
        ),
    ]
