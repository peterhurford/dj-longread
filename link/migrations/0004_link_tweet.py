# Generated by Django 3.1.6 on 2021-07-07 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0003_auto_20210321_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='tweet',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]