# Generated by Django 2.0.4 on 2018-04-14 22:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twitter_models', '0005_auto_20180414_0548'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediction',
            name='estimate',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.PROTECT, to='twitter_models.Estimate'),
            preserve_default=False,
        ),
    ]
