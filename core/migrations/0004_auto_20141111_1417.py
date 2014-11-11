# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20141110_1913'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_num', models.IntegerField()),
                ('base_points', models.IntegerField()),
                ('friend_points', models.IntegerField(default=b'0')),
                ('time_points', models.IntegerField(default=b'0')),
                ('status', models.IntegerField(default=-1, choices=[(0, b'Active'), (-1, b'Future'), (1, b'Completed')])),
                ('difficulty', models.IntegerField(default=0, choices=[(0, b'Easy'), (1, b'Moderate'), (2, b'Hard')])),
                ('est_date', models.DateField(auto_now_add=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('completion_date', models.DateField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Goal',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GoalGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ownerid', models.ForeignKey(to='core.LyfeUser')),
            ],
            options={
                'db_table': 'GoalGroup',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='goal',
            name='goal_id',
            field=models.ForeignKey(to='core.GoalGroup'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='goal',
            unique_together=set([('id', 'order_num')]),
        ),
    ]
