# Generated by Django 3.0.4 on 2020-05-17 05:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0002_auto_20200517_0517'),
    ]

    operations = [
        migrations.RenameField(
            model_name='link',
            old_name='linked',
            new_name='liked',
        ),
    ]
