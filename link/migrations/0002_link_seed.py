# Generated by Django 3.0.4 on 2020-06-15 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='seed',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]
