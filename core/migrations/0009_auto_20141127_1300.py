# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20141119_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='difficulty',
            field=models.IntegerField(default=0, choices=[(0, b'easy'), (1, b'moderate'), (2, b'hard')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='goal',
            name='status',
            field=models.IntegerField(default=-1, choices=[(0, b'active'), (-1, b'future'), (1, b'completed')]),
            preserve_default=True,
        ),
    ]
