# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-30 21:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relationaldb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournamentparticipantissuance',
            name='participant',
        ),
        migrations.DeleteModel(
            name='TournamentParticipantIssuance',
        ),
    ]
