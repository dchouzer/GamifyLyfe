# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20141111_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(max_length=50)),
                ('creator_uid', models.ForeignKey(to='core.LyfeUser')),
            ],
            options={
                'db_table': 'Comment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('request_time', models.DateTimeField(auto_now_add=True)),
                ('approval_time', models.DateTimeField(null=True, blank=True)),
                ('recipient_id', models.ForeignKey(related_name='recipient_id', to='core.LyfeUser')),
                ('requester_id', models.ForeignKey(related_name='requester_id', to='core.LyfeUser')),
            ],
            options={
                'db_table': 'Friend',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('creator_id', models.ForeignKey(to='core.LyfeUser')),
            ],
            options={
                'db_table': 'Group',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.ForeignKey(to='core.Group')),
                ('user_id', models.ForeignKey(to='core.LyfeUser')),
            ],
            options={
                'db_table': 'Membership',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=50)),
                ('worth', models.IntegerField()),
                ('user_id', models.ForeignKey(to='core.LyfeUser')),
            ],
            options={
                'db_table': 'Reward',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RewardTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('reward_id', models.ForeignKey(to='core.Reward')),
            ],
            options={
                'db_table': 'RewardTransaction',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShareSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sharee', models.CharField(default=b'public', max_length=20)),
                ('goal_id', models.ForeignKey(to='core.GoalGroup')),
            ],
            options={
                'db_table': 'ShareSetting',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(max_length=50)),
                ('goal_id', models.ForeignKey(to='core.GoalGroup')),
                ('user_id', models.ForeignKey(to='core.LyfeUser')),
            ],
            options={
                'db_table': 'Update',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sharesetting',
            unique_together=set([('goal_id', 'sharee')]),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('group_id', 'user_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='friend',
            unique_together=set([('requester_id', 'recipient_id')]),
        ),
        migrations.AddField(
            model_name='comment',
            name='update_id',
            field=models.ForeignKey(to='core.Update'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set([('creator_uid', 'update_id', 'timestamp')]),
        ),
    ]
