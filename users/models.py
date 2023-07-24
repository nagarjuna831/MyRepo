from django.db import models
from datetime import datetime
import os
import uuid
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail  
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, name, phone,company_name, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not password:
            raise ValueError('Password is required')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            company_name=company_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, name, phone, company_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, name, phone,company_name, **extra_fields)

    def create_superuser(self, email, password, name, phone, company_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, name, phone, company_name, **extra_fields)


def profile_dir_path(instance, filename):
    today = datetime.now()
    path = "users/{}/{}/{}/".format(today.year, today.month, today.day)
    extension = "." + filename.split('.')[-1]
    unique_id = str(uuid.uuid4())
    filename_reformat = unique_id + extension
    return os.path.join(path, filename_reformat)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=254)
    name = models.CharField(max_length=240)
    phone = models.CharField(max_length=50)
    profile = models.FileField(blank=False, upload_to=profile_dir_path)
    company_name = models.CharField(max_length=50, null=True, blank=True, default='')
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        

    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

        email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

        send_mail(
            # title:
            "Password Reset for {title}".format(title="Some website title"),
            # message:
            email_plaintext_message,
            # from:
            "noreply@somehost.local",
            # to:
            [reset_password_token.user.email]
        )


# @receiver(post_save, sender=User)
# def send_mail_on_create(sender, instance=None, created=False, **kwargs):

#     if created:
#         email=instance.email
#         context={'UserName': email,
#             'message': 'You have successfully registred '}
    
#         html_message = render_to_string('registration.html', context)
#         plain_message = strip_tags(html_message)
        
#         send_mail('Welcome to Epsumlabs',html_message, 'eform@epsumlabs.in', [email], html_message=html_message)       