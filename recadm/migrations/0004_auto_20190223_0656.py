# Generated by Django 2.2.dev20180928135712 on 2019-02-23 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recadm', '0003_auto_20190113_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usage',
            name='notes',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]
