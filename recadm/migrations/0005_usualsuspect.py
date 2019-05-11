# Generated by Django 2.2.dev20180928135712 on 2019-05-04 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subadd', '0008_auto_20190430_2009'),
        ('recadm', '0004_auto_20190223_0656'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsualSuspect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('dosage', models.DecimalField(decimal_places=3, max_digits=7)),
                ('notes', models.CharField(blank=True, max_length=512)),
                ('sub_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subadd.Substance')),
            ],
        ),
    ]