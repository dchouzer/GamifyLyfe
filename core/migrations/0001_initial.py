# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LyfeUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('cur_points', models.IntegerField()),
                ('total_points', models.IntegerField()),
                ('account_creation_date', models.DateField(auto_now_add=True)),
                ('last_active_date', models.DateField(auto_now=True)),
                ('last_fp_given', models.DateField()),
                ('avatar', models.FileField(upload_to=b'')),
            ],
            options={
                'db_table': 'LyfeUser',
            },
            bases=(models.Model,),
        ),
    ]
