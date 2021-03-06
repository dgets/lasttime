# Generated by Django 2.2.dev20180928135712 on 2019-01-14 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subadd', '0003_auto_20181111_0823'),
    ]

    operations = [
        migrations.CreateModel(
            name='DosageUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(max_length=5)),
                ('description', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='substance',
            name='units',
            field=models.CharField(default='mg', max_length=5),
        ),
    ]
