# Generated by Django 3.1.6 on 2021-11-27 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0008_auto_20211003_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='starred',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
