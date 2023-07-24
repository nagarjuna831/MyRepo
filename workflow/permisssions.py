from subscription.models import Billing
from django.shortcuts import get_object_or_404

from rest_framework import permissions


class WorkflowPermission(permissions.BasePermission):
    # for view permission
    def has_permission(self, request, view):

        if request.method == "GET":
            return True
        
        if request.method == 'POST':
            try:
                billing=Billing.objects.get(user=request.user.id)
                return True
            except:
                return False                   