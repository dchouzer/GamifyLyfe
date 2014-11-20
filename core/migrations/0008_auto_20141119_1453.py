# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20141116_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='name',
            field=models.CharField(default='name', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goalgroup',
            name='name',
            field=models.CharField(default='goalname', max_length=30),
            preserve_default=False,
        ),
    ]
