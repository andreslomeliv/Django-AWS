# Generated by Django 3.0.2 on 2020-08-21 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20200821_0224'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='verified',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
