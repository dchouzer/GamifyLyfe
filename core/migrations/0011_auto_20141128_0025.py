# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20141128_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lyfeuser',
            name='cur_points',
            field=models.IntegerField(default=b'0'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lyfeuser',
            name='total_points',
            field=models.IntegerField(default=b'0'),
            preserve_default=True,
        ),
    ]
