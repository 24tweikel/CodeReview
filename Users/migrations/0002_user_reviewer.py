# Generated by Django 3.2.7 on 2021-09-10 18:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reviewer',
            field=models.BooleanField(default=False),
        ),
    ]
