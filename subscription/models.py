from django.db import models
from django.utils import timezone


# Create your models here.
class Billing(models.Model):
    TYPE_CHOICES = (
        ("YES", "yes"),
        ("NO", "no")
    )

    TYPE_CHOICE = (
        ("Y", "y"),
        ("N", "n")
    )

    SUBSCRIPTION_CHOICE = (
        ("Free", "free"),
        ("Deluxe", "deluxe"),
        ("Ultimate", "ultimate"),
        ("Custom", "custom")
    )

    billing_name = models.CharField(max_length=254)
    contact_no = models.CharField(max_length=254)
    contact_person = models.CharField(max_length=254, default='', blank=True)
    designation = models.CharField(max_length=254, default='', blank=True)
    address = models.CharField(max_length=254, default='', blank=True)
    email = models.EmailField(max_length=254)
    gst_no = models.CharField(max_length=254, default="", null= True, blank=True)
    user = models.OneToOneField(to='users.user', on_delete=models.CASCADE, related_name='billig_user')
    date_added = models.DateTimeField(auto_now_add=True)
    active = models.CharField(max_length=20, choices=TYPE_CHOICES, default='YES')
    form_count = models.IntegerField(default=0)
    team_count = models.IntegerField(default=0)
    workflow_count = models.IntegerField(default=0)
    email_count = models.IntegerField(default=0)
    custome_form_count = models.CharField(max_length=20, choices=TYPE_CHOICE, default='N')
    e_signature_count = models.CharField(max_length=20, choices=TYPE_CHOICE, default='N')
    space_assign = models.CharField(max_length=254, default='')
    monthly_submission = models.IntegerField(default=0)
    payment_done = models.CharField(max_length=20, choices=TYPE_CHOICE, default='N')
    expiry_date = models.DateField(default=timezone.localdate)
    subscription_type = models.CharField(max_length=100,default="Free", choices=SUBSCRIPTION_CHOICE)
    duration = models.IntegerField(default=0, null=True, blank=True)


class BillingData(models.Model):
    billing = models.ForeignKey(to=Billing, on_delete=models.CASCADE, related_name='billig_data')
    content = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='billig_data_user', default=None,
                             blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


class BillingPayment(models.Model):

    SUBSCRIPTION_CHOICE = (
        ("Free", "free"),
        ("Deluxe", "deluxe"),
        ("Ultimate", "ultimate"),
        ("Custom", "custom")
    )

    hash_id = models.CharField(max_length=255,blank=True,default='', null=True)
    order_id = models.CharField(max_length=255,blank=True,default='', null=True)
    payment_status = models.CharField(max_length=255, default='')
    payment_id = models.CharField( max_length=255,blank = True,default=None, null=True)
    created_at = models.DateTimeField(auto_now=True)
    billing = models.ForeignKey(to=Billing, on_delete=models.CASCADE, related_name='billing_payment')
    subscription_type = models.CharField(max_length=100,default="Free", choices=SUBSCRIPTION_CHOICE)
    duration = models.IntegerField(default=0, null=True, blank=True)
    amount = models.IntegerField(default=0, blank=True, null=True)


class SubscriptionModel(models.Model):
    TYPE_CHOICE = (
        ("Y", "y"),
        ("N", "n")
    )

    name=models.CharField(max_length=255, default='')
    monthly_amount = models.IntegerField(default=0)
    yearly_amount = models.IntegerField(default=0)
    form_count = models.IntegerField(default=0)
    team_count = models.IntegerField(default=0)
    workflow_count = models.IntegerField(default=0)
    email_count = models.IntegerField(default=0)
    custome_form_count = models.CharField(max_length=20, choices=TYPE_CHOICE, default='N')
    e_signature_count = models.CharField(max_length=20, choices=TYPE_CHOICE, default='N')
    space_assign = models.CharField(max_length=254, default='')
    monthly_submission = models.IntegerField(default=0)
