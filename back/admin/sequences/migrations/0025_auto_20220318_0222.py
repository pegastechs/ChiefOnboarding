# Generated by Django 3.2.12 on 2022-03-18 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequences', '0024_auto_20220310_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountprovision',
            name='additional_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='pendingadmintask',
            name='option',
            field=models.IntegerField(choices=[(0, 'No'), (1, 'Email'), (2, 'Slack')], max_length=12500, verbose_name='Send email or Slack message to extra user?'),
        ),
    ]
