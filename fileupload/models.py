from django.db import models
import uuid
import os
from datetime import datetime
from subscription.models import Billing
from django.contrib.auth import get_user_model
from django.conf import settings
media_root = settings.MEDIA_ROOT


def get_directory_size(path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    size_suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0        
    return total_size


def file_dir_path(instance,filename):
    today = datetime.now()
    try:
        if instance.user.id:
            user_id=instance.user.id
            billings=Billing.objects.get(user=user_id)
            data_assign=billings.space_assign
            path = "{}/{}/{}/{}/".format(billings.billing_name,today.year, today.month, today.day)
            # data=get_directory_size(media_root+"/"+billings.billing_name)
            # print(media_root+"/"+billings.billing_name)
            # print(data,media_root)
            extension = "." + filename.split('.')[-1]
            unique_id = str(uuid.uuid4())
            filename_reformat = unique_id + extension
            return os.path.join(path, filename_reformat) 
          
    except Exception as e:
        path = "documents/{}/{}/{}/".format(today.year, today.month, today.day)
        extension = "." + filename.split('.')[-1]
        unique_id = str(uuid.uuid4())
        filename_reformat = unique_id + extension
        return os.path.join(path, filename_reformat)
    
        
class Files(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    file = models.FileField(blank=False, upload_to=file_dir_path)
    date_added = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False)
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='file_data_user', blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    
    
    def __unicode__(self):
        return self.file.name
    

    def save(self, *args, **kwargs):
        self.name = self.file.name
        self.type = self.file.name.split('.')[-1].lower()
        super(Files, self).save(*args, **kwargs)
    

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