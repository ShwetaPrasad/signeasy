# Generated by Django 3.1.7 on 2021-03-01 18:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0012_auto_20210301_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='access',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='documents.document'),
        ),
    ]
