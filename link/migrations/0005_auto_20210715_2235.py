# Generated by Django 3.1.6 on 2021-07-16 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0004_link_tweet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='aggregator',
            field=models.CharField(default='Custom', max_length=2000),
        ),
        migrations.AlterField(
            model_name='link',
            name='liked',
            field=models.IntegerField(blank=True, default=-1, null=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='tweet',
            field=models.IntegerField(default=0),
        ),
    ]