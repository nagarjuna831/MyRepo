# Generated by Django 4.2 on 2023-05-26 11:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('monthly_amount', models.IntegerField(default=0)),
                ('yearly_amount', models.IntegerField(default=0)),
                ('form_count', models.IntegerField(default=0)),
                ('team_count', models.IntegerField(default=0)),
                ('workflow_count', models.IntegerField(default=0)),
                ('email_count', models.IntegerField(default=0)),
                ('custome_form_count', models.CharField(choices=[('Y', 'y'), ('N', 'n')], default='N', max_length=20)),
                ('e_signature_count', models.CharField(choices=[('Y', 'y'), ('N', 'n')], default='N', max_length=20)),
                ('space_assign', models.CharField(default='', max_length=254)),
                ('monthly_submission', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='billing',
            name='duration',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='billing',
            name='expiry_date',
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AddField(
            model_name='billing',
            name='payment_done',
            field=models.CharField(choices=[('Y', 'y'), ('N', 'n')], default='N', max_length=20),
        ),
        migrations.AddField(
            model_name='billing',
            name='subscription_type',
            field=models.CharField(choices=[('Free', 'free'), ('Deluxe', 'deluxe'), ('Ultimate', 'ultimate'), ('Custom', 'custom')], default='Free', max_length=100),
        ),
        migrations.AlterField(
            model_name='billing',
            name='address',
            field=models.CharField(blank=True, default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='billing',
            name='contact_person',
            field=models.CharField(blank=True, default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='billing',
            name='designation',
            field=models.CharField(blank=True, default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='billing',
            name='gst_no',
            field=models.CharField(blank=True, default='', max_length=254, null=True),
        ),
        migrations.CreateModel(
            name='BillingPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_id', models.CharField(max_length=255,blank=True, default='', null=True)),
                ('order_id', models.CharField(max_length=255,blank=True, default='', null=True)),
                ('payment_status', models.CharField(default='', max_length=255)),
                ('payment_id', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('subscription_type', models.CharField(choices=[('Free', 'free'), ('Deluxe', 'deluxe'), ('Ultimate', 'ultimate'), ('Custom', 'custom')], default='Free', max_length=100)),
                ('duration', models.IntegerField(blank=True, default=0, null=True)),
                ('amount', models.IntegerField(blank=True, default=0, null=True)),
                ('billing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_payment', to='subscription.billing')),
            ],
        ),
    ]
