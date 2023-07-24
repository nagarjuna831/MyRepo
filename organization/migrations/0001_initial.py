# Generated by Django 4.1 on 2023-04-24 12:57

from django.db import migrations, models
import organization.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('OWNER', 'Owner'), ('ADMIN', 'Admin'), ('REPORTER', 'Reporter')], default='REPORTER', max_length=20)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('is_delete', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('logo', models.FileField(upload_to=organization.models.update_filename)),
                ('about', models.CharField(blank=True, max_length=500)),
                ('website', models.URLField()),
                ('panel_access_url', models.CharField(max_length=500, unique=True)),
                ('email', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('is_delete', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
    ]