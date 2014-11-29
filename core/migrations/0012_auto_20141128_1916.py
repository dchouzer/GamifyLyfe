# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20141128_0025'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Document',
        ),
        migrations.AlterField(
            model_name='goal',
            name='order_num',
            field=models.IntegerField(default=b'0'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='goal',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'active'), (-1, b'future'), (1, b'completed')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lyfeuser',
            name='avatar',
            field=models.FileField(default=b'./default.jpg', upload_to=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='update',
            name='goal_id',
            field=models.ForeignKey(to='core.Goal'),
            preserve_default=True,
        ),
    ]
