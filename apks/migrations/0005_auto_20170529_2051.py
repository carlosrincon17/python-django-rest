# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-29 20:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apks', '0004_auto_20170529_1740'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Token',
        ),
        migrations.AddField(
            model_name='apk',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
