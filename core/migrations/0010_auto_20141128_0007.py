# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0009_auto_20141127_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='lyfeuser',
            name='user',
            field=models.ForeignKey(default=-1, to=settings.AUTH_USER_MODEL, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='goal',
            name='name',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lyfeuser',
            name='avatar',
            field=models.FileField(default=b'settings.MEDIA_ROOT/files/default.jpg', upload_to=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lyfeuser',
            name='username',
            field=models.CharField(max_length=30, serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='update',
            name='content',
            field=models.CharField(max_length=500),
            preserve_default=True,
        ),
    ]
