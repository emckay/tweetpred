# Generated by Django 2.0.3 on 2018-03-26 05:26

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('screen_name', models.CharField(max_length=100)),
                ('dow', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('s3_key', models.CharField(max_length=100)),
                ('s3_bucket', models.CharField(max_length=100)),
                ('data_fetched_at', models.DateTimeField()),
                ('archived', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_params', django.contrib.postgres.fields.jsonb.JSONField()),
                ('hyper_params', django.contrib.postgres.fields.jsonb.JSONField()),
                ('params', django.contrib.postgres.fields.jsonb.JSONField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='twitter_models.Account')),
                ('data_file', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='twitter_models.DataFile')),
            ],
        ),
    ]
