# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20141110_1750'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lyfeuser',
            old_name='name',
            new_name='username',
        ),
    ]
