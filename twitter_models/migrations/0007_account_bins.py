# Generated by Django 2.0.4 on 2018-04-16 00:55

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_models', '0006_prediction_estimate'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='bins',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
            preserve_default=False,
        ),
    ]
