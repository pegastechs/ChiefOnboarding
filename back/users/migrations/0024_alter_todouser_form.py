# Generated by Django 3.2.12 on 2022-02-26 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_alter_user_seen_updates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todouser',
            name='form',
            field=models.JSONField(default=list),
        ),
    ]
