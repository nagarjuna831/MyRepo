# Generated by Django 4.1 on 2023-04-24 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('Create', 'Create'), ('Read', 'Read'), ('Update', 'Update'), ('Delete', 'Delete'), ('Login', 'Login'), ('Logout', 'Logout'), ('Login Failed', 'Login Failed')], max_length=15)),
                ('action_time', models.DateTimeField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Success', 'Success'), ('Failed', 'Failed')], default='Success', max_length=7)),
                ('data', models.JSONField(default=dict)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
    ]
