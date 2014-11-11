# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lyfeuser',
            name='avatar',
            field=models.FileField(null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lyfeuser',
            name='last_fp_given',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
