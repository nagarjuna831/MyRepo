from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from datetime import datetime
import uuid
import os


def update_filename(instance, filename):
    today = datetime.now()
    path = "logo/{}/{}/{}/".format(today.year, today.month, today.day)
    extension = "." + filename.split('.')[-1]
    unique_id = str(uuid.uuid4())
    filename_reformat = unique_id + extension
    return os.path.join(path, filename_reformat)


class Organization(models.Model):
    name = models.CharField(max_length=300, blank=False)
    logo = models.FileField(blank=False, upload_to=update_filename)
    about = models.CharField(max_length=500, blank=True)
    website = models.URLField()
    panel_access_url = models.CharField(max_length=500, blank=False, unique=True)
    email = models.CharField(max_length=100, blank=False)
    phone = models.CharField(max_length=20, blank=False)
    admin = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='organization_admin')
    is_verified = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        if self.is_delete:
            return
        self.is_delete = True
        self.save()


class Members(models.Model):
    MEMBER_TYPES = (('OWNER', 'Owner'),
                    ('ADMIN', 'Admin'),
                    ('REPORTER', 'Reporter'))
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE, related_name='member_organization')
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE, related_name='member_user')
    type = models.CharField(max_length=20, choices=MEMBER_TYPES, default='REPORTER')
    added_by = models.ForeignKey(to='users.User', on_delete=models.CASCADE, related_name='member_added_by', null=True,
                                 blank=True, default=None)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        if self.is_delete:
            return
        self.is_delete = True
        self.save()


@receiver(post_save, sender=Organization)
def create_organization_owner(sender, instance, **kwargs):
    Members.objects.create(organization=instance, user=instance.admin, type='OWNER', added_by=instance.admin)