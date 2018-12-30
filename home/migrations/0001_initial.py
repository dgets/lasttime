# Generated by Django 2.2.dev20180928135712 on 2018-12-06 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HeaderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motto', models.CharField(max_length=40)),
                ('mission', models.CharField(max_length=180)),
            ],
        ),
        migrations.CreateModel(
            name='NavInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=20)),
                ('link_text', models.CharField(max_length=20)),
            ],
        ),
    ]
