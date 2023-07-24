from rest_framework import permissions
from commons.models import UserPermissionsFormdata, UserPermissionsTemplate
from commons.serializers import UserPermissionsTemplateSerializer, UserPermissionsSerializer
import json
from datetime import date
from subscription.models import Billing
from django.shortcuts import get_object_or_404

class CustomeTemplatePermission(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.method == 'GET':
            templatepermission=UserPermissionsTemplate.objects.filter(user_id=request.user.id)
            if templatepermission:
                templatepermission1=UserPermissionsTemplateSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                create=data['add']
                edit=data['edit']
                view=data['view']
                if view == 'Y':
                    return True

            else:
                return True        
        
        if request.method == 'POST':
            
            if request.data['label'] in request.data:
                templatepermission=UserPermissionsTemplate.objects.filter(project_id=request.data['project'], user_id=request.user.id)
                if templatepermission:
                    templatepermission1=UserPermissionsTemplateSerializer(templatepermission,many=True)
                    templatepermission2=templatepermission1.data
                    templatepermission3=json.loads(json.dumps(templatepermission2))
                    data=templatepermission3[0]
                    create=data['add']
                    edit=data['edit']
                    view=data['view']
                    delete=data['remove']
                    if create == 'Y':
                        return True
            else:
                return True
           
        
        if request.method == 'PUT':
            if request.data['label'] in request.data:
                templatepermission=UserPermissionsTemplate.objects.filter(project_id=request.data['project'] ,user_id=request.user.id)
                if templatepermission:
                    templatepermission1=UserPermissionsTemplateSerializer(templatepermission,many=True)
                    templatepermission2=templatepermission1.data
                    templatepermission3=json.loads(json.dumps(templatepermission2))
                    data=templatepermission3[0]
                    create=data['add']
                    edit=data['edit']
                    view=data['view']
                    delete=data['remove']
                    if edit == 'Y':
                        return True
            else:
                
                return True            
            
        
        if request.method == 'DELETE':
            templatepermission=UserPermissionsTemplate.objects.filter(user_id=request.user.id)
            if templatepermission:
                templatepermission1=UserPermissionsTemplateSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                create=data['add']
                edit=data['edit']
                view=data['view']
                delete=data['remove']
                if delete == 'Y':
                    return True

            else:
                return True
                            
        if request.method == 'PATCH':
            return True

class CustomeFormDataPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET': 
            templatepermission=UserPermissionsFormdata.objects.filter(user_id=request.user.id)
            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                last_date=data['last_date']
                today = date.today()
                view=data['view']
                if last_date:
                    if view == 'Y' and last_date >= str(today) :
                        return True

                elif view == 'Y':
                    return True

        if request.method == 'POST':
            templatepermission=UserPermissionsFormdata.objects.filter(template_id=request.data['template'],user_id=request.user.id)

            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                last_date=data['last_date']
                today = date.today()
                create=data['add']
                edit=data['edit']
                view=data['view']
                delete=data['remove']
                if last_date:
                    if create == 'Y' and last_date >= str(today) :
                        return True

                elif create == 'Y':
                    return True        
        
            else:
                return {'details':'template not available'}

        if request.method == 'PUT':
            templatepermission=UserPermissionsFormdata.objects.filter(template_id=request.data['template'],user_id=request.user.id)

            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                last_date=data['last_date']
                today = date.today()
                edit=data['edit']
                if last_date:
                    if edit == 'Y' and last_date >= str(today) :
                        return True

                elif edit == 'Y':
                    return True

            else:
                return {'details':'template not available'}

        if request.method == 'DELETE':
            templatepermission=UserPermissionsFormdata.objects.filter(user_id=request.user.id)
            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                last_date=data['last_date']
                today = date.today()
                delete=data['remove']
                if last_date:
                    if delete == 'Y' and last_date >= str(today) :
                        return True
                elif delete == 'Y' :
                    return True

          
class CustomeCommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            templatepermission=UserPermissionsFormdata.objects.filter(user_id=request.user.id)
            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                view=data['view']
                if view == 'Y':
                    return True
        
        if request.method == 'POST':
            templatepermission=UserPermissionsFormdata.objects.filter(user_id=request.user.id)

            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                create=data['add']
                if create == 'Y':
                    return True
        
        if request.method == 'PUT':
            templatepermission=UserPermissionsFormdata.objects.filter(user_id=request.user.id)
            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                edit=data['edit']
                if edit == 'Y':
                    return True
        
        if request.method == 'DELETE':
            templatepermission=UserPermissionsFormdata.objects.filter(user_id=request.user.id)
            if templatepermission:
                templatepermission1=UserPermissionsSerializer(templatepermission,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                delete=data['remove']
                if delete == 'Y':
                    return True                               