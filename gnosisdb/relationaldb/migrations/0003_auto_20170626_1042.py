# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-26 10:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relationaldb', '0002_auto_20170626_1040'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='oracle',
            unique_together=set([('factory', 'creator')]),
        ),
    ]
