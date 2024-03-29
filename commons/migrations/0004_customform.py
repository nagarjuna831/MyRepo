# Generated by Django 4.1 on 2023-05-26 11:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forms', '0003_initial'),
        ('commons', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_form_data', models.TextField()),
                ('custom_template_type', models.CharField(blank=True, default='', max_length=225, null=True)),
                ('active', models.BooleanField(default=False)),
                ('form_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='custom_form_relation', to='forms.template')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_form', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
