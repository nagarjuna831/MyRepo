from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from subscription.models import Billing


class Workflow(models.Model):
    label = models.CharField(max_length=100, blank=True, db_index=True, default='')
    description = models.CharField(max_length=255, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='workflow_data_user')
    billing = models.ForeignKey(to=Billing, on_delete=models.CASCADE, related_name='billing_workflow', blank=True,
                                null=True, default=None)

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


class TemplateWorkflow(models.Model):
    workflow = models.ForeignKey(to=Workflow, on_delete=models.CASCADE, related_name='assigned_workflow')
    template = models.ForeignKey(to='forms.Template', on_delete=models.CASCADE, related_name='assigned_template')
    description = models.CharField(max_length=300, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)


class State(models.Model):
    label = models.CharField(max_length=100, blank=True, db_index=True, default='')
    description = models.CharField(max_length=255, blank=True, default='')
    completion = models.CharField(max_length=100, blank=True, default='')
    workflow = models.ForeignKey(to=Workflow, on_delete=models.CASCADE, related_name='state_workflow')
    is_initial = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

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


class Transition(models.Model):
    label = models.CharField(max_length=100, blank=True, db_index=True, default='')
    description = models.CharField(max_length=255, blank=True, default='')
    origin_state = models.ForeignKey(to=State, on_delete=models.CASCADE, related_name='origin_transition_state')
    destination_state = models.ForeignKey(to=State, on_delete=models.CASCADE,
                                          related_name='destination_transition_state')
    workflow = models.ForeignKey(to=Workflow, blank=False, on_delete=models.CASCADE, related_name='transition_workflow',
                                 default='')
    properties = models.CharField(max_length=255, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

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


class WorkflowInstance(models.Model):
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE, related_name='instance_user')
    form_data = models.ForeignKey(to='forms.FormData', on_delete=models.CASCADE, related_name='instance_form_data')
    current_state = models.ForeignKey(to=State, on_delete=models.CASCADE, related_name='instance_state')
    date_added = models.DateTimeField(auto_now_add=True)


class WorkflowInstanceLog(models.Model):
    user = models.ForeignKey(to='users.User', on_delete=models.CASCADE, related_name='instance_log_user')
    form_data = models.ForeignKey(to='forms.FormData', on_delete=models.CASCADE, related_name='instance_log_form_data')
    transition = models.ForeignKey(to=Transition, on_delete=models.CASCADE, related_name='instance_log_transition')
    comment = models.CharField(max_length=300, blank=True, default='')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)


@receiver(post_save, sender='forms.FormData')
def create_workflow_instance(sender, instance, created, **kwargs):
    try:
        template_workflow = TemplateWorkflow.objects.get(template=instance.template.id)
        state = State.objects.get(is_initial=True, workflow=template_workflow.workflow.id)
        if created:
            if instance.user:
                WorkflowInstance.objects.create(user=instance.user, form_data=instance, current_state=state)
            else:
                WorkflowInstance.objects.create(user=template_workflow.template.user, form_data=instance,
                                                current_state=state)
    except:
        pass


@receiver(post_save, sender=WorkflowInstanceLog)
def update_workflow_instance(sender, instance, created, **kwargs):
    workflow_instance = WorkflowInstance.objects.get(form_data=instance.form_data)
    workflow_instance.user = instance.user
    workflow_instance.current_state = instance.transition.destination_state
    workflow_instance.save()


class WorkflowStateMember(models.Model):
    user = models.ForeignKey(to='users.user', on_delete=models.CASCADE, related_name='workflow_state_user')
    template = models.ForeignKey(to='forms.Template', on_delete=models.CASCADE,
                                 related_name='workflow_assigned_template')
    state = models.ForeignKey(to=State, on_delete=models.CASCADE, related_name='workflow_instance_state')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)

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
