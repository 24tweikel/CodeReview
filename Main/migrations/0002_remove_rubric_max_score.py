# Generated by Django 3.2.7 on 2021-09-28 17:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('Main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rubric',
            name='max_score',
        ),
    ]