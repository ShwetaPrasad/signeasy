# Generated by Django 3.1.7 on 2021-03-01 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_document_isedit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='isEdit',
            new_name='isLocked',
        ),
    ]
