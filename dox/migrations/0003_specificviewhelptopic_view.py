# Generated by Django 2.2.dev20180928135712 on 2019-02-23 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dox', '0002_auto_20190120_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='specificviewhelptopic',
            name='view',
            field=models.CharField(default='', max_length=40),
        ),
    ]
