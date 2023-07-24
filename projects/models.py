from email.policy import default
from django.db import models
from datetime import datetime
from subscription.models import Billing


class Project(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='projects_data_user')
    organization = models.ForeignKey(to='organization.Organization', on_delete=models.CASCADE,
                                     related_name='organization_project', blank=True, null=True, default=None)

    billing = models.ForeignKey(to=Billing, on_delete=models.CASCADE,related_name='billing_project',blank=True, null=True, default=None)                                 
    
    
    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        if self.is_delete: return
        self.is_delete = True
        self.save()