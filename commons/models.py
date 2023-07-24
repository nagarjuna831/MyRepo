from datetime import datetime
from enum import unique
from gettext import install
from os import remove
from pyexpat import model
import uuid
from venv import create
from django.db import models
from projects.models import Project
from organization.models import Organization
from forms.models import Template, Fields
from django.db.models.signals import post_save 
from django.dispatch import receiver


class UserPermissionsTemplate(models.Model):

    PERMISSION_CHOICES = (
        ("OWNER", "Owner"),
        ("MAINTAINER", "Maintainer"),
        ("REPORTER", "Reporter"),
        ("INDIVIDUAL", "Individual"),

    )

    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='permissions_user_template')
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name='project_permissions_template', null=True,
                                blank=True, default=None)
                                                                                                 
    level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='OWNER')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)    
    add=models.CharField(max_length=255, blank=True, default='')
    edit=models.CharField(max_length=255, blank=True, default='')
    remove=models.CharField(max_length=255, blank=True, default='')
    view=models.CharField(max_length=255, blank=True, default='')
    last_date=models.DateField(null=True)
    

    def save(self, *args, **kwargs):
        if self.level == 'INDIVIDUAL':
            self.add = 'Y'
            self.edit = 'Y'
            self.remove = 'Y'
            self.view = 'Y'
            super(UserPermissionsTemplate, self).save(*args, **kwargs)

        if self.level == 'MAINTAINER':
            self.add = 'Y'
            self.edit = 'Y'
            self.remove = 'N'
            self.view = 'Y'
            super(UserPermissionsTemplate, self).save(*args, **kwargs)

        if self.level == 'REPORTER':
            self.add = 'N'
            self.edit = 'N'
            self.remove = 'N'
            self.view = 'Y'
            super(UserPermissionsTemplate, self).save(*args, **kwargs) 
        
        if self.level == 'OWNER':
            self.add = 'Y'
            self.edit = 'Y'
            self.remove = 'Y'
            self.view = 'Y'
            super(UserPermissionsTemplate, self).save(*args, **kwargs)


    def __iter__(self):
        return [ self. user,
                 self.project, 
                 self.level,
                 self.add, 
                 self.edit, 
                 self.view,
                 self.remove ]                           

    class Meta:
       ordering = ('-date_added',)

    class Meta:
        unique_together = ('user','project')
    
    @receiver(post_save, sender=Project)
    def update_workflow_instance(sender, instance,created, **kwargs):
        permisssion_instance=Project.objects.get(id=instance.id)
        project1=permisssion_instance.id
        if created:
            UserPermissionsTemplate.objects.create(user=instance.user,project_id=project1)


class DefaultValue(models.Model):                
    deafult_value=models.CharField(max_length=300, blank=True, null=True ,default='')
    field=models.ForeignKey(to=Fields, on_delete=models.CASCADE, related_name='field_permissions' , null=True,blank=True, default=None)


class UserPermissionsFormdata(models.Model):
    
    PERMISSION_CHOICES = (
        ("OWNER", "Owner"),
        ("MAINTAINER", "Maintainer"),
        ("REPORTER", "Reporter"),
        ("INDIVIDUAL", "Individual"),

    )

    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='permissions_user')
    template=models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='template_permissions')                                                                 
    level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='OWNER')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)   
    add=models.CharField(max_length=255, blank=True, default='')
    edit=models.CharField(max_length=255, blank=True, default='')
    remove=models.CharField(max_length=255, blank=True, default='')
    view=models.CharField(max_length=255, blank=True, default='')
    last_date=models.DateField(null=True)
    deafult_value=models.ManyToManyField(to=DefaultValue,  null=True,blank=True, default=None)
    

    def save(self, *args, **kwargs):
        if self.level == 'INDIVIDUAL':
            self.add = 'Y'
            self.edit = 'Y'
            self.remove = 'Y'
            self.view = 'Y'
            super(UserPermissionsFormdata, self).save(*args, **kwargs)
            
        if self.level == 'MAINTAINER':
            self.add = 'Y'
            self.edit = 'Y'
            self.remove = 'N'
            self.view = 'Y'
            super(UserPermissionsFormdata, self).save(*args, **kwargs)

        if self.level == 'REPORTER':
            self.add = 'N'
            self.edit = 'N'
            self.remove = 'N'
            self.view = 'Y'
            super(UserPermissionsFormdata, self).save(*args, **kwargs)

        if self.level == 'OWNER':
            self.add = 'Y'
            self.edit = 'Y'
            self.remove = 'Y'
            self.view = 'Y'
            super(UserPermissionsFormdata, self).save(*args, **kwargs)

    def __iter__(self):
        return [ self. user,
                 self.template,
                 self.level,
                 self.add, 
                 self.edit, 
                 self.view,
                 self.remove ]                           

    class Meta:
        ordering = ('-date_added',)

    class Meta:
        unique_together = ( 'user','template',)    
    

    @receiver(post_save, sender=Template)
    def update_workflow_instance(sender, instance,created, **kwargs):
        permisssion_instance=Template.objects.get(id=instance.id)
        template=permisssion_instance.id
        project1=permisssion_instance.project
        user_id=permisssion_instance.user.id
        if project1:
            project_user=Project.objects.get(id=project1.id)
            data=UserPermissionsTemplate.objects.filter(project_id=project_user.id)
            if created:
                for i in data:
                    UserPermissionsFormdata.objects.create(user_id=i.user.id,template_id=template,level=i.level)
        else:
            if created:
                UserPermissionsFormdata.objects.create(user_id=user_id,template_id=template,level='OWNER')
    
    
    # @receiver(post_save, sender=UserPermissionsTemplate)
    # def update_workflow_instance(sender, instance,created, **kwargs):
    #     print(instance.id)
    #     permisssion_instance=UserPermissionsTemplate.objects.get(id=instance.id)
    #     print(permisssion_instance.project_id)
    #     project1=permisssion_instance.project_id
    #     user_id=permisssion_instance.user_id
    #     level=permisssion_instance.level
    #     print(project1,user_id,level)
    #     if project1:
    #         project_data=Template.objects.filter(project=project1)
    #         if created:
    #             for i in project_data:
    #                 data=UserPermissionsFormdata.objects.all(user_id=user_id,template_id=i.id)
    #                 if data:
    #                     pass
    #                 else:   
    #                   UserPermissionsFormdata.objects.create(user_id=user_id,template_id=i.id,level=level)
    #     else:
    #         if created:
    #             UserPermissionsFormdata.objects.create(user_id=user_id,template_id=i.id,level='OWNER')
                            

class UserPermissionsFields(models.Model):
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='permissions_user_fields')
    template=models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='template_permissions_fields')
    deafult_value=models.CharField(max_length=300, blank=True, null=True ,default='')
    field=models.ForeignKey(to=Fields, on_delete=models.CASCADE, related_name='field_permissions_user', null=True,blank=True,default=12 )


class Team(models.Model):
    template = models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='teams_permission_template', null=True,blank=True, default=None)               
    name=models.CharField(max_length=300)
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='user_team' ,default=None,null=True,blank=True)


class TeamPermission(models.Model):
    TYPE_CHOICES = (
        ("0", "0"),
        ("1", "1")
        )
    team=models.ForeignKey(to=Team , on_delete=models.CASCADE, related_name='team_permissions_team', null=True,blank=True, default=None)
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='permissions_user_team')
    team_lead= models.CharField(max_length=20, choices=TYPE_CHOICES, default='0' )
    
    class Meta:
        unique_together = ( 'user','team',) 


class ConfigurationSettings(models.Model):
    TYPE_CHOICES = (
        ("0", "0"),
        ("1", "1")
        )

    logo_url=models.CharField(max_length=300, blank=True, null=True ,default='')
    sign_up=models.CharField(max_length=20, choices=TYPE_CHOICES, default='1' )
    title_name=models.CharField(max_length=300, blank=True, null=True ,default='')


class Notification(models.Model):
    TYPE_CHOICES = (
        ("0", "0"),
        ("1", "1")
        )

    user=models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='notification_user')
    message=models.CharField(max_length=300, blank=True, null=True ,default='')
    notification=models.CharField(max_length=20, choices=TYPE_CHOICES, default='0' )
    date_added = models.DateTimeField(auto_now_add=True)
    view_date=models.DateTimeField(auto_now_add=True)

class CustomForm(models.Model):
    user=models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='custom_form')
    custom_form_data = models.TextField()
    form_id = models.OneToOneField(Template, on_delete=models.CASCADE, related_name='custom_form_relation')
    custom_template_type= models.CharField(max_length=225, blank=True, default='',null=True)
    active = models.BooleanField(default=False)