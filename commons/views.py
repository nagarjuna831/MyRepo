from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import generics, viewsets, permissions, status
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.http import HttpResponse
from django.db.models import Q
from django.db import connection
from forms.models import FormData
from forms.serializers import FormDataSerializer
from subscription.models import Billing
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
# Create your views here.
import ast 


class PermissionListViewSet(viewsets.ModelViewSet):
    serializer_class = UserPermissionsSerializer
    queryset = UserPermissionsFormdata.objects.all()

    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                data=self.request.body.decode()
                data=ast.literal_eval(data)
                deafult_value=data['deafult_value']
                if deafult_value:
                    for i in deafult_value:
                        print(i)
                        UserPermissionsFields.objects.create(deafult_value=i['deafult_value'],field_id=i['field'],template_id=data['template'],user_id=data['user'])
                else:
                    UserPermissionsFields.objects.create(deafult_value=None,field_id=None,template_id=data['template'],user_id=data['user'])
                    
                
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError :
            return Response({'error': 'Duplicate key value violates unique constraint'},status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        permission= self.get_object()
        permission.delete()
        return Response(data='delete success')


class PermissionUpdateApi(generics.UpdateAPIView):
    serializer_class = UserPermissionUpdatesSerializer
    queryset = UserPermissionsFormdata.objects.all()
    lookup_field = 'id'
    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class PermissionDeleteApi(generics.DestroyAPIView):
    serializer_class = UserPermissionUpdatesSerializer
    queryset = UserPermissionsFormdata.objects.all()
    lookup_field = 'id'

    def perform_destroy(self, instance):
        # custom logic to perform before deletion
        instance.delete()


class  PermissionListView(generics.ListAPIView):
    serializer_class =  UserPermissionsSerializer
    def get_queryset(self):
        return  UserPermissionsFormdata.objects.filter(id=self.kwargs['id'])


class  PermissionTemplateListView(generics.ListAPIView):
    pagination_class=None
    serializer_class =  UserPermissionsSerializer
    def get_queryset(self):
        return  UserPermissionsFormdata.objects.filter(template=self.kwargs['id'], user=self.request.user.id)      


class TemplatePermissionListViewSet(viewsets.ModelViewSet):
    serializer_class = UserPermissionsTemplateSerializer
    queryset = UserPermissionsTemplate.objects.all()
    def destroy(self, request, *args, **kwargs):
        permission= self.get_object()
        permission.delete()
        return Response(data='delete success')


class  TemplatePermissionListView(generics.ListAPIView):
    serializer_class =  UserPermissionsSerializer
    def get_queryset(self):
        return  UserPermissionsTemplate.objects.filter(id=self.kwargs['id'])


class FieldPermissionListViewSet(viewsets.ModelViewSet):
    serializer_class = UserPermissionsFieldSerializer
    queryset = UserPermissionsFields.objects.all()
    def destroy(self, request, *args, **kwargs):
        permission= self.get_object()
        permission.delete()
        return Response(data='delete success')


class  FieldPermissionListView(generics.ListAPIView):
    serializer_class = UserPermissionsFieldSerializer
    def get_queryset(self):
        return  UserPermissionsFields.objects.filter(id=self.kwargs['id'])


class TeamListViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    
    def create(self, request):
        try:
            billing= Billing.objects.get(user=request.user.id)
            if billing:
                billing_accont=billing.active
                team_count=billing.team_count
                if billing_accont == "YES":
                    teams_count=Team.objects.filter(user=request.user.id).count()
                    if team_count >= teams_count+1:
                        serializer = self.get_serializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        self.perform_create(serializer)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"message":"your billing  account have not permission to create teams"})

                else:    
                    return Response({"message":"your billing  account is not active"})
        except:
            return Response({"message":"create your billing account"},status=status.HTTP_400_BAD_REQUEST)
    

    def destroy(self, request, *args, **kwargs):
        permission= self.get_object()
        permission.delete()
        return Response(data='delete success')


class TeamListUserView(generics.ListAPIView):
    serializer_class = TeamUsersSerializer
    def get_queryset(self):
        user=self.request.user.id
        return  Team.objects.filter(user=user)


class  TeamListView(generics.ListAPIView):
    serializer_class = TeamSerializer
    def get_queryset(self):
        return  Team.objects.filter(id=self.kwargs['id'])


class TeamListUserLeadView(generics.ListAPIView):
    serializer_class = TeamsUserSerializer
    def get_queryset(self):
        user=self.request.user.id
        return  TeamPermission.objects.filter(user=user,team_lead=1)


class TeamPermissionListViewSet(viewsets.ModelViewSet):
    serializer_class = TeamPermissionSerializer
    queryset = TeamPermission.objects.all()
    def destroy(self, request, *args, **kwargs):
        permission= self.get_object()
        permission.delete()
        return Response(data='delete success')


class  TeamPermissionListView(generics.ListAPIView):
    serializer_class = TeamMemberSerializer
    def get_queryset(self):
        return  TeamPermission.objects.filter(team_id=self.kwargs['id'])


# Utility function
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
    ]

####

class  TeamPermissionTemplateListView(generics.ListAPIView):
    def get(self,request, *args, **kwargs):
        user=self.request.user.id
        val="""SELECT distinct public.commons_team.template_id,public.forms_template.label FROM public.commons_team right join public.commons_teampermission on public.commons_team.id=public.commons_teampermission.team_id right join public.forms_template on public.forms_template.id=public.commons_team.template_id WHERE public.commons_teampermission.team_lead='1' and public.commons_teampermission.user_id="""+str(user)
        with connection.cursor() as cursor:
            cursor.execute(val)
            rows = dictfetchall(cursor)
        

        return Response({'data':rows})


class  TeamTemplateView(generics.ListAPIView):
    serializer_class = TeamTemplateSerializer
    queryset = Team.objects.all()


class  TeamTemplateMemberView(generics.ListAPIView):

   def get(self,request, *args, **kwargs):
        user=self.request.user.id
        template_id=self.kwargs['template_id']
        val="""SELECT team_id FROM public.commons_team left join public.commons_teampermission on public.commons_team.id=public.commons_teampermission.team_id WHERE template_id="""+str(template_id)+""" and user_id="""+str(user)+""" and team_lead='1' """
        with connection.cursor() as cursor:
            cursor.execute(val)
            rows = dictfetchall(cursor)
        

        for i in rows:
            val="""SELECT public.users_user.* from public.commons_teampermission left join public.users_user on public.commons_teampermission.user_id=public.users_user.id WHERE team_id="""+str(i['team_id'])
            with connection.cursor() as cursor:
                cursor.execute(val)
                rows = dictfetchall(cursor)
        

        return Response({'data':rows})


class TeamFormDataView(generics.ListAPIView):
    serializer_class = FormDataSerializer
    def get_queryset(self):
        user=self.request.user.id
        template_id=self.kwargs['template_id']  
        val="""SELECT team_id FROM public.commons_team left join public.commons_teampermission on public.commons_team.id=public.commons_teampermission.team_id WHERE template_id="""+str(template_id)+""" and user_id="""+str(user)+""" and team_lead='1' """
        with connection.cursor() as cursor:
            cursor.execute(val)
            rows = dictfetchall(cursor)
        

        for i in rows:
            val="""SELECT user_id from public.commons_teampermission WHERE team_id="""+str(i['team_id'])
            with connection.cursor() as cursor:
                cursor.execute(val)
                rows = dictfetchall(cursor)
        
    
        startdate=self.request.query_params.get("startdate",None)
        enddate=self.request.query_params.get("enddate",None)

        if startdate and enddate and rows:
            for i in rows:
                print(i,startdate,enddate)
                return FormData.objects.filter(template_id=self.kwargs['template_id'], is_delete=False).filter(date_added__date__range=(startdate, enddate)).filter(user=i['user_id'])

        elif startdate and enddate :
            return  FormData.objects.filter(template_id=self.kwargs['template_id'], is_delete=False).filter(date_added__date__range=(startdate, enddate))
        elif rows:
            for i in rows:
                return FormData.objects.filter(template_id=self.kwargs['template_id'], is_delete=False).filter(user=i['user_id'])
        else:
            return FormData.objects.filter(template_id=self.kwargs['template_id'], is_delete=False)


class   UserPermissionsFieldsView(generics.ListAPIView):
    serializer_class = UserPermissionsFieldSerializer

    def get(self,request, *args, **kwargs):
        user=self.request.user.id
        val="""SELECT deafult_value from public.commons_userpermissionsfields WHERE template_id="""+str(self.kwargs['template_id'])+"""and field_id="""+str(self.kwargs['field_id'])+"""and user_id="""+str(user)
        
        with connection.cursor() as cursor:
            cursor.execute(val)
            rows = dictfetchall(cursor)
        
        if rows:
            return Response({'data':rows})
        else:
            val="""SELECT deafult_value from public.forms_fields WHERE template_id="""+str(self.kwargs['template_id'])+"""and id="""+str(self.kwargs['field_id'])+"""and user_id="""+str(user)
            with connection.cursor() as cursor:
                cursor.execute(val)
                rows = dictfetchall(cursor)

            return Response(rows)     


class ConfigurationSettingsViewSet(viewsets.ModelViewSet):
    permission_classes=[permissions.AllowAny]
    serializer_class = ConfigurationSettingsSerializer
    queryset = ConfigurationSettings.objects.all()
    def destroy(self, request, *args, **kwargs):
        permission= self.get_object()
        permission.delete()
        return Response(data='delete success')

 
class  TeamPermissionLeadListView(generics.ListAPIView):
    serializer_class = TeamLeadSerializer
    def get_queryset(self):
        user=self.request.user.id
        return  TeamPermission.objects.filter(user_id=user, team_lead=1)


class  TeamPermissionUserListView(generics.ListAPIView):
    serializer_class = TeamUserSerializer
    def get_queryset(self):
        return  TeamPermission.objects.filter(team_id=self.kwargs['id'])  


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    def destroy(self, request, *args, **kwargs):
        permission= self.get_object()
        permission.delete()
        return Response(data='delete success')

class CustomFormView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CustomFormSerializer

    # def get_form_data_as_dict(self):
    #     return json.load(self.form_data)

    def get(self, request):
        try:
            user = request.user.id
            custom_forms = CustomForm.objects.filter(user=user)
            data = []
            for custom_form  in custom_forms:
                data.append({
                    'custom_template_type':custom_form.custom_template_type,
                    'form_id': custom_form.form_id.id,
                    'custom_form_data': custom_form.custom_form_data,
                    'active': custom_form.active
                })
            return Response({
                'status': True,
                "data": data,
                "message": "Fetch custom form successfully!"
            })
        except ObjectDoesNotExist:
            return Response({
                'status': True,
                "data": [],
                "message": "This user does not have any custom form!"
            }, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                "message": "Something went worng!"
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            user = request.user.id
            # get all custom form of this user
            custom_forms = CustomForm.objects.filter(user=user)
            for custom_form in custom_forms:
                custom_form.active = False
                custom_form.save()
            data = request.data
            print(data['form_id'])
            data['custom_form_data'] = json.dumps(data['custom_form_data'])
            data['user'] = user
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'results': serializer.data,
                    'message': 'The custom form is successfully created!'
                })
            else:
                return Response({
                    'status': False,
                    'error': serializer.errors
                }, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                
                'message': 'Something went wrong!'
            },status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request):
        try:
            user = request.user.id
            data = request.data
            data['user'] = user
            data['custom_form_data'] = json.dumps(data['custom_form_data'])
            form_id = data['form_id']

            # get all custom form of this user
            custom_forms = CustomForm.objects.filter(user=user)
            for custom_form in custom_forms:
                custom_form.active = False
                custom_form.save()
            custom_form = CustomForm.objects.filter(form_id=form_id).first()
            if custom_form:
                serializer = self.serializer_class(custom_form, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'status': True,
                        'results': serializer.data,
                        'message': "Custom form update successfully!"
                    })
                else:
                    return Response({
                        'status':False,
                        'message': serializer.errors
                    }, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'status': False,
                    "message": "Invalid form id!"
                }, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                "message": "Something went worng!"
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomFormListView(generics.ListAPIView, generics.DestroyAPIView):
    serializer_class = CustomFormSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CustomForm.objects.filter(form_id=self.kwargs['id']).filter(user=self.request.user.id)
    def delete(self, request, *args, **kwargs):
        try:
            instance = CustomForm.objects.filter(form_id=self.kwargs['id'])
            print(instance)
            instance.delete()
            return Response({
                'success': True,
                'message': "Custom form successfully deleted !"
            },status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                'success': True,
                'error': "This form is not exist !"
            },status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                'success': True,
                'error': "Something went wrong !"
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)