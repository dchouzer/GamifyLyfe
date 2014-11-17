# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lyfeuser',
            name='id',
        ),
        migrations.AlterField(
            model_name='lyfeuser',
            name='username',
            field=models.CharField(max_length=20, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
