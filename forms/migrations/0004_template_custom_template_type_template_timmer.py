# Generated by Django 4.1 on 2023-05-26 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='custom_template_type',
            field=models.CharField(blank=True, default='', max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='template',
            name='timmer',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
