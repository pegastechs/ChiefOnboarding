# Generated by Django 3.2.12 on 2022-04-08 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0010_delete_scheduledaccess'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesstoken',
            name='name',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
    ]
