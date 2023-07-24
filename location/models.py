from django.db import models
from datetime import datetime
# Create your models here.

class UserTracking(models.Model):
    lat = models.CharField(max_length=100, blank=False)
    long = models.CharField(max_length=255, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    user= models.CharField(max_length=100, blank=False)
    
    class Meta:
        ordering = ('-id',)


    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        if self.is_delete: return
        self.is_delete = True
        self.save()
    