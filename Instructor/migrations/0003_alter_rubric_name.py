# Generated by Django 4.0 on 2021-12-17 12:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('Instructor', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rubric',
            name='name',
            field=models.CharField(help_text='The name the students will use to pick a rubric when requesting a review',
                                   max_length=50),
        ),
    ]