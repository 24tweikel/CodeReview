# Generated by Django 3.2.7 on 2021-10-08 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0006_alter_review_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='scores',
        ),
    ]
