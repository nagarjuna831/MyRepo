from datetime import datetime
import uuid
from django.db import models
from projects.models import Project
import os
from datetime import datetime
from django.dispatch import receiver
from django.urls import reverse
from django.core.mail import send_mail  
from django.db.models.signals import post_save, pre_save
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from subscription.models import Billing,BillingData


def file_dir_path(instance, filename):
    today = datetime.now()
    path = "documents/file/{}/{}/{}/".format(today.year, today.month, today.day)
    extension = "." + filename.split('.')[-1]
    unique_id = str(uuid.uuid4())
    filename_reformat = unique_id + extension
    return os.path.join(path, filename_reformat)


class Template(models.Model):
    label = models.CharField(max_length=100, blank=True, db_index=True, default='')
    description = models.CharField(max_length=255, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name='project_template', null=True,
                                blank=True, default=None)
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='template_user')
    organization = models.ForeignKey(to='organization.Organization', on_delete=models.CASCADE,
                                     related_name='organization_template', blank=True, null=True, default=None)

    image_header = models.FileField(blank=False, null=True, upload_to=file_dir_path ,default='')
    image_footer = models.FileField(blank=False, null=True, upload_to=file_dir_path ,default='')
    billing = models.ForeignKey(to=Billing, on_delete=models.CASCADE,related_name='billing_template',blank=True, null=True, default=None)
    email_formdatas= models.BooleanField(default=False)
    email_workflows= models.BooleanField(default=False)
    email_comments=  models.BooleanField(default=False)
    type=models.CharField(max_length=255, blank=True, default='')
    custom_template_type = models.CharField(max_length=225, blank=True, default='',null=True)
    timmer = models.IntegerField(default=0, null=True, blank=True)
        
    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.label

    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        if self.is_delete: return
        self.is_delete = True
        self.save()


class EmailNotification(models.Model):
    template=models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='template_email_notification')
    email_formdata= models.BooleanField(default=False)
    email_workflow= models.BooleanField(default=False)
    email_comment=  models.BooleanField(default=False)


class Validation(models.Model):
    type = models.CharField(max_length=50,default='', null=True)
    expression = models.TextField(default='', null=True)
    error_message = models.TextField(default='', null=True)


class Fields(models.Model):
    TYPE_CHOICES = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4")
    )

    template = models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='template_fields')
    label = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=300, blank=False)
    placeholder = models.CharField(blank=True, max_length=300)
    tooltip = models.CharField(max_length=300, blank=True)
    mandatory = models.BooleanField(default=False)
    sequence = models.IntegerField(default=1)
    display_in_main_view = models.BooleanField(default=True)
    validation = models.ForeignKey(to=Validation, on_delete=models.CASCADE, related_name='field_validation',
                                   blank=True, null=True, default=None)
    master_data_code = models.CharField(max_length=300, default='')
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='field_user')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    check_unique= models.BooleanField(default=False)
    unique_type=models.CharField(max_length=20, choices=TYPE_CHOICES, default='1' )
    auto_sum=models.BooleanField(default=False)
    deafult_value=models.CharField(max_length=300, blank=True, null=True ,default='')
    style= models.CharField(max_length=300, blank=True, null=True ,default='')
    api=models.URLField(max_length=1000,blank=True,null=True,default='')
    values= models.CharField(max_length=1000, blank=True, null=True,default='')
    ocr_view= models.BooleanField(default=False)
    table_data=models.CharField(max_length=1000, blank=True, null=True,default='')
    card_no = models.IntegerField(default=1, null=True, blank=True)


    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return self.label

    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        if self.is_delete: return
        self.is_delete = True
        self.save()
    
    def set_values(self, value):
        self.values = ','.join(value)

    def get_values(self):
        return self.values.split(',')
    
class Data(models.Model):
    field = models.ForeignKey(to=Fields, on_delete=models.CASCADE, related_name='field')
    value = models.TextField()

    class Meta:
        ordering = ('field__sequence',)


class FormData(models.Model):
    template = models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='template_form')
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='form_data_user', null=True,
                             blank=True, default=None)                   
    data = models.ManyToManyField(Data,verbose_name="data")
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    lock_status= models.CharField(max_length=300, default='N')

    class Meta:
        ordering = ('-date_added',)

    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    def delete(self, *args, **kwargs):
        if self.is_delete: return
        self.is_delete = True
        self.save()

    def __str__(self) -> str:
        return f"{self.template.id}"


class FormDataComment(models.Model):
    formdata = models.ForeignKey(to=FormData, on_delete=models.CASCADE, related_name='formdata_data')
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='form_data_comment_user', null=True,
                             blank=True, default=None)                 
    comment = models.TextField(blank=True)
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
        if self.is_delete: return
        self.is_delete = True
        self.save()


class ShareForm(models.Model):
    PERMISSION_CHOICES = (
        ("ANYONE_WITH_LINK", "Anyone with link"),
        ("RESTRICTED", "Restricted"),
    )
    SCOPE_CHOICES = (
        ("ADD", "Add"),
        ("VIEW", "View"),
    )
    label = models.CharField(max_length=300, default='', blank=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    template = models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='shared_template')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='shared_user')
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='RESTRICTED')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='VIEW')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
   

    def update(self, *args, **kwargs):
        kwargs.update({'date_updated': datetime.now()})
        super().update(*args, **kwargs)
        return self

    class Meta:
        ordering = ['-id']

    def delete(self, *args, **kwargs):
        if self.is_delete: return
        self.is_delete = True
        self.save()


class TemplateFieldStyle(models.Model):
    template = models.ForeignKey(to=Template, on_delete=models.CASCADE, related_name='template_style', null=True,
                                blank=True, default=None)
    fileds = models.ForeignKey(to=Fields, on_delete=models.CASCADE, related_name='field_style', null=True,
                                blank=True, default=None)
    style= models.CharField(max_length=300, blank=True, null=True ,default='')


from commons.models import UserPermissionsFormdata,Team,TeamPermission
from commons.serializers import UserPermissionsSerializer,TeamSerializer,TeamPermissionSerializer
@receiver(post_save, sender=FormData)
def send_mail_on_create(sender, instance=None, created=False, **kwargs):
    email_list=[]
    user=instance.user
    template=instance.template.id
    billing=Template.objects.get(id=template)
    email_formdata=billing.email_formdatas
    if email_formdata == True:
        for i in UserPermissionsFormdata.objects.filter(template_id=template, level="OWNER"):
            email_list.append(i.user.email)
        

        for i in Team.objects.filter(template_id=template):
            for j in TeamPermission.objects.filter(team_id=i ,team_lead=1):
                email_list.append(j.user.email)
    
    
        for i in email_list:
            if created:
                BillingData.objects.create(email=i, billing=billing.billing, content="data insert in  forms" ,user= user, date_added=datetime.now)
            context={'UserName': i,
                'message': 'You have successfully registred '}
        
            html_message = render_to_string('registration.html', context)
            plain_message = strip_tags(html_message)
            send_mail('Welcome to Epsumlabs',html_message, 'eform@epsumlabs.in', [i], html_message=html_message)


@receiver(post_save, sender=FormDataComment)
def update_workflow_instance(sender, instance,created, **kwargs):
    email_list=[]
    formdata=instance.formdata.id
    formdata=FormData.objects.get(id=formdata)
    email_list.append(formdata.user)
    template=formdata.template
    billing=Template.objects.get(id=template.id)
    email_comment=billing.email_comments
    if email_comment == False:
        for i in UserPermissionsFormdata.objects.filter(template_id=template.id, level="OWNER"):
            email_list.append(i.user.email)

        for i in Team.objects.filter(template_id=template):
            for j in TeamPermission.objects.filter(team_id=i ,team_lead=1):
                email_list.append(j.user.email)
        print(email_list)
        for i in email_list:
            context={'UserName': i,
                'message': instance.comment}
        
            html_message = render_to_string('registration.html', context)
            plain_message = strip_tags(html_message)
            send_mail('Welcome to Epsumlabs',plain_message, 'eform@epsumlabs.in', [i], html_message=html_message)
    