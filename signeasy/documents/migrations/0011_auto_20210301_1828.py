# Generated by Django 3.1.7 on 2021-03-01 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0010_auto_20210301_1206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='isLocked',
            new_name='is_locked',
        ),
    ]