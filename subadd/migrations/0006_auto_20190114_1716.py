# Generated by Django 2.2.dev20180928135712 on 2019-01-14 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subadd', '0005_auto_20190114_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='substance',
            name='units',
            field=models.CharField(max_length=5),
        ),
    ]