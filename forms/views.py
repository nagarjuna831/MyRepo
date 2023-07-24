from urllib import response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import generics, viewsets, permissions, status
from .serializers import *
from .models import Template, Fields, FormData
from workflow.models import WorkflowInstance, Transition
from workflow.serializers import TransitionSerializer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filters import TemplateFilter, FieldsFilter
from rest_framework import filters
from rest_framework.generics import GenericAPIView
import json
import csv
from django.http import HttpResponse
from django.http import Http404
from .permissions import *
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from datetime import date
from django.db import connection
from projects.serializers import ProjectSerializer
from workflow.models import TemplateWorkflow, WorkflowStateMember
from workflow.serializers import TemplateWorkflowSerializer
from systemlog.utility import ActivityLogMixin
from rest_framework.generics import DestroyAPIView


class OneByOneItems(PageNumberPagination):
    page_size = 10
    def get_paginated_response(self, data):
        return Response(OrderedDict([
             ('lastPage', self.page.paginator.count),
             ('countItemsOnPage', self.page_size),
             ('current', self.page.number),
             ('next', self.get_next_link()),
             ('previous', self.get_previous_link()),
             ('results', data)
         ]))


class DynamicSearchFilter(filters.SearchFilter):

    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])


class FormListsView(ActivityLogMixin, generics.ListAPIView):
    pagination_class=None
    serializer_class = TemplateSerializer
    def get_queryset(self):
        user = self.request.user.id
        return Template.objects.filter(user_id=user).filter(is_delete=False)

    def get_log_message(self, request) -> str:
        return f" get all form list  successfully"    


class FormListView(ActivityLogMixin, generics.ListCreateAPIView):
    pagination_class=OneByOneItems
    permission_classes=[CustomeTemplatePermission,]
    serializer_class = TemplateSerializer
    queryset = Template.objects.filter(is_delete=False)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = TemplateFilter
    ordering_fields = ('date_added', 'label')
    ordering = ('-id',)
    search_fields = ('label',  'description')
    

    def create(self, request, *args,**kwargs):
        billing= Billing.objects.filter(user=request.user.id)
        forms_count=Template.objects.filter(is_delete=False,user=request.user.id).count()
        if billing:
            billing= BillingSerializer(billing,many=True)
            billing=billing.data
            billing=json.loads(json.dumps(billing))
            billing_accont=billing[0]['active']
            form_count=billing[0]['form_count']
            if billing_accont == "YES":
                if form_count>=forms_count+1:
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message":" your billing account have no enough forms"},status=status.HTTP_400_BAD_REQUEST)
            
            else:    
                return Response({"message":" your billing account is not active"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"create your billing account"},status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, *args, **kwargs):
        try:
            self.pagination_class=OneByOneItems
            user = self.request.user
            data=UserPermissionsFormdata.objects.filter(user_id=self.request.user.id )
            page=self.request.query_params.get("page",None)
            
            if data:
                templatepermission1=UserPermissionsSerializer(data,many=True)
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3
                data_list=[]
                count=0
                for i in data: 
                    newdata=Template.objects.filter(id=i['template']).filter(is_delete=False)
                    newdata1=TemplateSerializer(newdata,many=True)
                    newdata4=newdata1.data
                    newdata3=json.loads(json.dumps(newdata4))
                    current_user_data_count=FormData.objects.filter(user_id=self.request.user.id,template=i['template']).count()
                    if current_user_data_count and newdata3:
                        current_user_data=FormData.objects.filter(user_id=self.request.user.id,template=i['template'])
                        current_user_dataa=FormDataSerializer(current_user_data, many=True)
                        Datas=current_user_dataa.data
                        Datass=json.loads(json.dumps(Datas))
                        current_user_date_added=Datass[-1]['date_added']    
                        current_user_date_updated=Datass[-1]['date_updated']
                        project_name=newdata3[0]['project']
                        if project_name == None:
                            project_name
                        else:
                            name=Project.objects.filter(id=project_name).filter(is_delete=False)
                            projects=ProjectSerializer(name,many=True)
                            Datas=projects.data
                            Datass=json.loads(json.dumps(Datas))
                            project_name=Datass[0]['name']
                        
                        newdata3[0].update({'project_name':project_name,'current_user_data_count':current_user_data_count,'current_user_date_added':current_user_date_added,'current_user_date_updated':current_user_date_updated})
                        data_list.extend(newdata3)
                        count +=1
                    elif newdata3:
                        project_name=newdata3[0]['project']
                        if project_name == None:
                            project_name
                        else:
                            name=Project.objects.filter(id=project_name).filter(is_delete=False)
                            projects=ProjectSerializer(name,many=True)
                            Datas=projects.data
                            Datass=json.loads(json.dumps(Datas))
                            project_name=Datass[0]['name']

                        newdata3[0].update({'project_name':project_name,'current_user_data_count':0,'current_user_date_added':None,'current_user_date_updated':None})
                        data_list.extend(newdata3)
                        count +=1

                if page != None:
                    pages = self.paginate_queryset(data_list[::-1])
                    return Response({'count': count,'data':pages})
                else:
                    return Response({'count': count,'data':data_list[::-1]})

            data=Template.objects.filter(user=user).filter(is_delete=False)
            count=data.count()
            newdata1=TemplateSerializer(data,many=True)
            newdata4=newdata1.data
            newdata3=json.loads(json.dumps(newdata4))
            data_list=[]
            for i in newdata3:
                project_name=i['project']
                if project_name == None:
                    project_name
                else:
                    print(project_name)
                    name=Project.objects.filter(id=project_name).filter(is_delete=False)
                    projects=ProjectSerializer(name,many=True)
                    Datas=projects.data
                    Datass=json.loads(json.dumps(Datas))
                    project_name=Datass[0]['name']    
                current_user_data_count=FormData.objects.filter(user_id=self.request.user.id,template=i['id']).count()
                current_user_data=FormData.objects.filter(user_id=self.request.user.id,template=i['id'])
                current_user_dataa=FormDataSerializer(current_user_data, many=True)
                Datas=current_user_dataa.data
                Datass=json.loads(json.dumps(Datas))
                current_user_date_added=Datass[-1]['date_added']
                current_user_date_updated=Datass[-1]['date_updated']
                i.update({'project_name':project_name,'current_user_data_count':current_user_data_count,'current_user_date_added':current_user_date_added,'current_user_date_updated':current_user_date_updated})
                data_list.extend(i)
            if page != None:
                pages = self.paginate_queryset(data_list[::-1])
                return Response({'count': count,'data':pages})
            else:
                return Response({'count': count,'data':data_list[::-1]})
        except:
            return Response({'message':'template not available'},status=status.HTTP_400_BAD_REQUEST)


    def get_log_message(self, request) -> str:
        return f" get all form list  successfully"      


class TemplateUserListView(ActivityLogMixin, generics.ListAPIView):
    serializer_class = TemplateSerializer

    def get_queryset(self):
        return Template.objects.filter(user_id=self.kwargs['id']).filter(is_delete=False)

              
class FormUpdateList(ActivityLogMixin, generics.RetrieveUpdateAPIView):
    permission_classes=[CustomeTemplatePermission,]
    serializer_class = TemplateSerializer
    queryset = Template.objects.filter(is_delete=False)
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)
    lookup_field = 'id'

    def  get(self,request,id=None):
        data=TemplateWorkflow.objects.filter(template=self.kwargs['id'])
        if data:
            datas=TemplateWorkflowSerializer(data,many=True)
            datas=datas.data
            data=json.loads(json.dumps(datas))
            template=data[0]['workflow']
            templates=Template.objects.filter(id=self.kwargs['id']).filter(is_delete=False)
            template_data=TemplateSerializer(templates,many=True)
            template_data=template_data.data
            template_data=json.loads(json.dumps(template_data))
            datas=(template_data[0])
            datas.update({'workflow':template})
            return Response(datas)
            
        else:
            templates=Template.objects.filter(id=self.kwargs['id']).filter(is_delete=False)
            template_data=TemplateSerializer(templates,many=True)
            template_data=template_data.data
            template_data=json.loads(json.dumps(template_data))
            datas=(template_data[0])
            datas.update({'workflow':None})
            return Response(datas)


class FormDeleteApiView(APIView):
    permission_classes=[CustomeTemplatePermission,]
    
    def delete(self, request, id):
        print(request.user)
        try:
            article = Template.objects.get(id=id)
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"message":"data not found"})    


class FieldListViewSet(ActivityLogMixin,generics.ListCreateAPIView):
    serializer_class = FieldsSerializer
    queryset = Fields.objects.filter(is_delete=False)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = FieldsFilter
    ordering_fields = ('date_added', 'type', 'label')
    ordering = ('-id',)
    search_fields = ('template', 'label', 'type', 'date_added')


class FieldUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FieldsSerializer
    queryset = Fields.objects.filter(is_delete=False)
    lookup_field = 'id'


class FieldsListView(ActivityLogMixin, generics.ListAPIView):
    pagination_class=None
    serializer_class = FieldsSerializer
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)
    def get_queryset(self):
        return Fields.objects.filter(template_id=self.kwargs['id'], is_delete=False).filter(is_delete=False)


class FormDataListViewSet(ActivityLogMixin, viewsets.ModelViewSet):
    permission_classes=[CustomeFormDataPermission,]
    serializer_class = FormDataSerializer
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)
    queryset = FormData.objects.filter(is_delete=False)
    
    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        data=UserPermissionsFormdata.objects.filter(user_id=self.request.user.id, template_id=request.data['template'] )
        if data:
            templatepermission1=UserPermissionsSerializer(data,many=True)
            templatepermission2=templatepermission1.data
            templatepermission3=json.loads(json.dumps(templatepermission2))
            data=templatepermission3[0]
            if data:
                if data['level'] == 'INDIVIDUAL':
                    if request.data['lock_status'] == 'Y':
                        serializer = self.get_serializer(instance, data=request.data, partial=partial)
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)
                        return Response(serializer.data)

                    else :
                        return Response({"detail": "This Data is locked, unlock to delete"}, status=status.HTTP_400_BAD_REQUEST)

                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    

    # def delete(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response({'message': 'Data was successfully deleted.'})
    

    def destroy(self, request, *args, **kwargs):
        print(self.request.user.id,"hhhh")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data=UserPermissionsFormdata.objects.filter(user_id=self.request.user.id, template_id=serializer.data['template'] )
            print("yes")
            print(data)
            if data:
                templatepermission1=UserPermissionsSerializer(data,many=True)
                print("yes")
                templatepermission2=templatepermission1.data
                templatepermission3=json.loads(json.dumps(templatepermission2))
                data=templatepermission3[0]
                if data:
                    if data['level'] == 'INDIVIDUAL':
                        if serializer.data['lock_status'] == 'Y':
                            self.perform_destroy(instance)
                            print("yes data deleteded") 
                            return Response({"detail": "data  delete sucessfully"}, status=status.HTTP_204_NO_CONTENT)
                        else :
                            return Response({"detail": "This Data is locked, unlock to delete"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    self.perform_destroy(instance)
                    print("yes data delete") 
                    return Response({"detail": "data  delete sucessfully"}, status=status.HTTP_204_NO_CONTENT)     

            self.perform_destroy(instance)
            print("yes Data Delete")                        
            return Response({"detail": "data  delete sucessfully"}, status=status.HTTP_204_NO_CONTENT)
        except:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)


class FormDataDeleteApiView(generics.DestroyAPIView):
    serializer_class = FormDataSerializer
    queryset = FormData.objects.filter(is_delete=False)
    lookup_field = 'id'

    def perform_destroy(self, instance):
        # custom logic to perform before deletion
        instance.delete()
   
               
class FormDataListView(ActivityLogMixin, generics.ListAPIView):
    pagination_class=OneByOneItems
    permission_classes=[CustomeFormDataPermission,]
    serializer_class = FormDataSerializer
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)
         
    def get(self,request,id=None):
      
        self.pagination_class=OneByOneItems
        data=UserPermissionsFormdata.objects.filter(user_id=self.request.user.id, template_id=self.kwargs['id'] )
        if data:  
            templatepermission1=UserPermissionsSerializer(data,many=True)
            templatepermission2=templatepermission1.data
            templatepermission3=json.loads(json.dumps(templatepermission2))
            data=templatepermission3[0]
            current_user=data['level']
            user= User.objects.filter(id=self.request.user.id)
            userdata=UsersSerializer(user,many=True)
            Userdata=userdata.data
            UserData=json.loads(json.dumps(Userdata))
            userdatas=UserData[0]
            userdatas['level']=current_user
            view=data['view']
            if view == 'Y':
                if current_user == "INDIVIDUAL":
                    formdata=FormData.objects.filter(template_id=self.kwargs['id'], user_id=self.request.user.id, is_delete=False)
                    count=formdata.count()
                    formdata=FormDataSerializer(formdata,many=True)
                    formdata=formdata.data
                    datas=json.loads(json.dumps(formdata))
                    datass=datas
                    page = self.paginate_queryset(datass)
                    return Response({'count':count,'data':page,'current_user':userdatas})

                else:
                    formdata=FormData.objects.filter(template_id=self.kwargs['id'], is_delete=False)
                    count=formdata.count()
                    formdata=FormDataSerializer(formdata,many=True)
                    formdata=formdata.data
                    datas=json.loads(json.dumps(formdata))
                    datass=datas
                    page = self.paginate_queryset(datass)
                    return Response({'count':count,'data':page,'current_user':userdatas})
        

        formdata=FormData.objects.filter(template_id=self.kwargs['id'], is_delete=False)
        count=formdata.count()
        formdata=FormDataSerializer(formdata,many=True)
        formdata=formdata.data
        datas=json.loads(json.dumps(formdata))
        datass=datas
        page = self.paginate_queryset(datass)
        return Response({'count':count,'data':page})
        

class FormDataActionView(ActivityLogMixin, generics.ListAPIView):
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)
    serializer_class = TransitionSerializer
    
    def get_queryset(self):
        try:
            workflow_instance = get_object_or_404(klass=WorkflowInstance, form_data=self.kwargs['id'])
            state_id=workflow_instance.current_state
            user_id= self.request.user.id
            data=WorkflowStateMember.objects.filter(state_id=state_id.id,user_id=user_id)
            
            if data:
                return Transition.objects.filter(origin_state=workflow_instance.current_state, is_delete=False)
            else:
                return()    
        except:        
           
            return()


class ShareFormViewSet(ActivityLogMixin, viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)
    serializer_class = ShareFormSerializer
    queryset = ShareForm.objects.filter(is_delete=False)


class TemplateSharedListView(ActivityLogMixin,generics.ListAPIView):
    serializer_class = ShareFormSerializer
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)

    def get_queryset(self):
        return ShareForm.objects.filter(template_id=self.kwargs['id'], is_delete=False)


class SharedFormDataListView(ActivityLogMixin, generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SharedFormDataSerializer
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)

    def get_queryset(self):
        today = str(datetime.now())
        share_form = ShareForm.objects.filter(token=self.kwargs['token'], start_time__lte=today, end_time__gte=today,
                                              is_delete=False)
        return share_form


class StoreSharedFormData(ActivityLogMixin,generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FormDataSerializer

    def post(self, request, *args, **kwargs):
        try:
            today = str(datetime.now())
            share_form = get_object_or_404(klass=ShareForm, scope='ADD', token=self.kwargs['token'], is_delete=False)
            if share_form:
                if share_form.permission == 'RESTRICTED' and self.request.user.is_anonymous:
                    return Response({'message': "You need to login to submit this form"}, status.HTTP_400_BAD_REQUEST)
                else:
                    form_data = request.data
                    form_data['template'] = share_form.template.id
                    serializer = self.get_serializer(data=form_data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({'message': "Form submitted successfully"}, status.HTTP_201_CREATED)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'The form submission is not allowed now'}, status.HTTP_201_CREATED)
        except ValidationError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class ViewSharedFormData(ActivityLogMixin,generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FormDataSerializer
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)

    def get_queryset(self):
        today = str(datetime.now())
        share_form = get_object_or_404(klass=ShareForm, scope='VIEW', token=self.kwargs['token'],
                                       start_time__lte=today, end_time__gte=today, is_delete=False)
        return FormData.objects.filter(template=share_form.template.id, is_delete=False)


class FormDataListViewDownload(ActivityLogMixin, GenericAPIView):
    serializer_class=FormDataSerializer
    
    def get(self, request,id=None, format=None):
        queryset = Template.objects.get(id=id)
        queryset_data = TemplateFilter(queryset)
        templatename=queryset_data.data
        Form =FormData.objects.filter(template_id=id, is_delete=False)
        serializer = FormDataSerializer(Form,many=True)
        Deta=serializer.data
        FormDeta=json.loads(json.dumps(Deta))
        FieldsData=Fields.objects.filter(template_id=id, is_delete=False)
        fields_data = FieldsSerializer(FieldsData,many=True)
        FieldsData=fields_data.data
        Fields_Data=json.loads(json.dumps(FieldsData))
        fieldnames=['counts']
        templatedatas=[]

        for fields in Fields_Data:
            fieldnames.append(fields['label'])

        fieldnames.extend(['Last Modified','user'])
        
        counts=0
        templatedataa=[]
        form_field_datas=[]
        valuess=[]
        for i in FormDeta:
            name=(i['user']['name'])
            if name:
                name=name
            else:
                name="Anonymous Users" 
            date_updated=(i['date_updated'])
            templatedataas={}
            values=[]    
            for j in (i['data']):
                for k in Fields_Data:
                    if (j['field_data']['id']) == k['id']:
                        key=(k['label'])
                        if k['auto_sum'] == True:
                            values.append(j['value'])
                        if key:
                            key=key
                        else:
                            key=''
                            print(key)
                        value=(j['value'])
                        data={key:value}
                        templatedataas.update(data)
            counts +=1
            templatedataas['counts']=counts     
            templatedataas['user']=name
            templatedataas['Last Modified']=date_updated
            templatedataa.append(templatedataas)
            valuess.append(values)
        print(valuess)    
        datass={}
        for fields in Fields_Data:
            datass.update({fields['label']:''})

                    

        datass.update({'counts':'Total','Last Modified':'','user':''})
        print(datass)
        templatedataa.append(datass)
        today = str(datetime.now().strftime('%Y-%m-%d'))                                 
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename= %s_%s.csv' %(templatename,today)
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(templatedataa)
        return response 


from django.db.models import Q
class FormDataSearchListView(ActivityLogMixin,generics.ListAPIView):
    serializer_class=FormDataSerializer

    def get(self,request, *args, **kwargs):
        # queryset=Data.objects.all()
        queryset1=FormData.objects.filter(template_id=self.kwargs['id']).filter(is_delete=False)
        field_id=request.query_params.get("field_id",None)
        value=request.query_params.get("value",None)
        if field_id and value:
            queryset1=queryset1.filter(Q(data__field_id=field_id)&Q(data__value__icontains=value))
            # data=Response(FormData.objects.filter(template_id=self.kwargs['id']).filter(is_delete=False).filter(Q(data__field_id=field_id)&Q(data__value__icontains=value)))
            queryset1= FormDataSerializer(queryset1,many=True)
            return Response(queryset1.data)
            
        else:
            data=queryset1
            data= FormDataSerializer(data,many=True)
            return Response(data.data)


        serializer=DataSerializer(queryset,many=True)
        formdata=json.loads(json.dumps(serializer.data))
        dataid=[]

        for x in formdata:
            dataid.append(x['id'])
        
        Formdata=[]
        template_id=self.kwargs['id']
        
        for y in dataid:
            queryset1=FormData.objects.filter(data=y).filter(template_id=self.kwargs['id']).filter(is_delete=False)
            serializer1=FormDataSerializer(queryset1,many=True)
            Formdata.append(serializer1.data)

        return Response({"data":Formdata})
        

class FormDataSearchView(ActivityLogMixin, generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class=DataSerializer
    def get(self,request, *args, **kwargs):
        today = str(datetime.now())
        share_form = get_object_or_404(klass=ShareForm, scope='VIEW', token=self.kwargs['token'],
                                        start_time__lte=today, end_time__gte=today, is_delete=False)
        if share_form:                                 
            queryset=Data.objects.all()
            field_id=request.query_params.get("field_id",None)
            value=request.query_params.get("value",None)

            if field_id and value:
                queryset=queryset.filter(field_id=field_id,value__icontains=value)
            else:
                queryset=Data.objects.all()


            serializer=DataSerializer(queryset,many=True)
            formdata=json.loads(json.dumps(serializer.data))
            dataid=[]

            for x in formdata:
                dataid.append(x['id'])
            
            Formdata=[]
            template_id=self.kwargs['id']
            
            for y in dataid:
                queryset1=FormData.objects.filter(data=y).filter(template_id=self.kwargs['id']).filter(is_delete=False)
                serializer1=FormDataSerializer(queryset1,many=True)
                Formdata.append(serializer1.data)
                          
            return Response(Formdata)
        else:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)     


class FormDataCommentView(ActivityLogMixin,generics.ListCreateAPIView):
    serializer_class = FormDataCommentSerializer
    queryset = FormDataComment.objects.filter(is_delete=False)


class FormDataCommentUpdateView(ActivityLogMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[CustomeCommentPermission,]
    serializer_class = FormDataCommentSerializer
    queryset = FormDataComment.objects.filter(is_delete=False)
    lookup_field = 'id'


class FormDataCommentListView(ActivityLogMixin, generics.ListAPIView):
    serializer_class = FormDataCommentSerializer
    filter_backends = (DjangoFilterBackend, DynamicSearchFilter)

    def get_queryset(self):
        return FormDataComment.objects.filter(formdata_id=self.kwargs['id'], is_delete=False)


class FormtUserListView(ActivityLogMixin, generics.ListAPIView):
    serializer_class = FormdataMemberSerializer
    def get_queryset(self):
        return  UserPermissionsFormdata.objects.filter(template_id=self.kwargs['id'])

    
class FormDataValidateView(ActivityLogMixin, generics.ListAPIView):
    serializer_class = FormDataSerializer
    def get(self,request, *args, **kwargs):
        data=Fields.objects.filter(is_delete=False, template_id=self.kwargs['template_id'], id=self.kwargs['field_id']  )
        if data:
            Data1=FieldsSerializer(data,many=True)
            fielddata=Data1.data
            fielddata=json.loads(json.dumps(fielddata))
            fielddata=fielddata[0]
            if fielddata['check_unique'] == True :
                if fielddata['unique_type'] == '1':
                    formdata=Data.objects.filter(field_id=self.kwargs['field_id'],value=self.kwargs['value'])
                    formdata=DataSerializer(formdata,many=True)
                    formdata=formdata.data
                    datas=json.loads(json.dumps(formdata))
                    if datas:
                        return Response({'status':True})
                    else:
                        return Response({'status':False})
                
                elif fielddata['unique_type'] == '2':
                    formdata=Data.objects.filter(field_id=self.kwargs['field_id'],value=self.kwargs['value'])
                    if formdata:
                        formdata=DataSerializer(formdata,many=True)
                        formdata=formdata.data
                        datas=json.loads(json.dumps(formdata))
                        data_id=datas[0]['id']
                        formdata_data=FormData.objects.filter(is_delete=False).filter(template_id=self.kwargs['template_id'],data=data_id)
                        if formdata_data:
                            formdata_data=FormDataSerializer(formdata_data,many=True)
                            formdata_data=formdata_data.data
                            formdata_data=json.loads(json.dumps(formdata_data))
                            date_added=formdata_data[0]['date_added'][0:10]
                            today = date.today()
                            user=formdata_data[0]['user']['id']
                            user_ID=self.request.user.id
                            print(user,user_ID)
                            if  date_added == str(today):
                                return Response({'status':True})
                            else:
                                return Response({'status':False})

                        return Response({'status':False})

                    return Response({'status':False}) 
                

                elif fielddata['unique_type'] == '3':
                    formdata=Data.objects.filter(field_id=self.kwargs['field_id'],value=self.kwargs['value'])
                    if formdata:
                        formdata=DataSerializer(formdata,many=True)
                        formdata=formdata.data
                        datas=json.loads(json.dumps(formdata))
                        data_id=datas[0]['id']
                        formdata_data=FormData.objects.filter(is_delete=False).filter(template_id=self.kwargs['template_id'],data=data_id)
                        if formdata_data:
                            formdata_data=FormDataSerializer(formdata_data,many=True)
                            formdata_data=formdata_data.data
                            formdata_data=json.loads(json.dumps(formdata_data))
                            today = date.today()
                            user=formdata_data[0]['user']['id']
                            user_ID=self.request.user.id
                            if  user == user_ID:
                                return Response({'status':True})
                            else:
                                return Response({'status':False})

                        return Response({'status':False})

                    return Response({'status':False}) 

                elif fielddata['unique_type'] == '4':
                    formdata=Data.objects.filter(field_id=self.kwargs['field_id'],value=self.kwargs['value'])
                    if formdata:
                        formdata=DataSerializer(formdata,many=True)
                        formdata=formdata.data
                        datas=json.loads(json.dumps(formdata))
                        data_id=datas[0]['id']
                        formdata_data=FormData.objects.filter(is_delete=False).filter(template_id=self.kwargs['template_id'],data=data_id)
                        if formdata_data:
                            formdata_data=FormDataSerializer(formdata_data,many=True)
                            formdata_data=formdata_data.data
                            formdata_data=json.loads(json.dumps(formdata_data))
                            today = date.today()
                            user=formdata_data[0]['user']['id']
                            date_added=formdata_data[0]['date_added'][0:10]
                            user_ID=self.request.user.id

                            if  user == user_ID and date_added == str(today):
                                return Response({'status':True})
                            else:
                                return Response({'status':False})

                        return Response({'status':False})

                    return Response({'status':False}) 

            else:
                return Response({'status':False})
        
        return Response({'status':False})


class FormDataView(ActivityLogMixin,generics.ListAPIView):
    permission_classes=[CustomeFormDataPermission,]
    serializer_class = FormDataSerializer
    def get_queryset(self):
        startdate=self.request.query_params.get("startdate",None)
        enddate=self.request.query_params.get("enddate",None)
        user=self.request.query_params.get("user",None)
        print(startdate,enddate,user)
        if startdate and enddate and user:

            return FormData.objects.filter(template_id=self.kwargs['id'], is_delete=False).filter(date_added__date__range=(startdate, enddate)).filter(user=user)

        elif startdate and enddate :
            return  FormData.objects.filter(template_id=self.kwargs['id'], is_delete=False).filter(date_added__date__range=(startdate, enddate))
        elif user:
            return FormData.objects.filter(template_id=self.kwargs['id'], is_delete=False).filter(user=user)
        else:
            return FormData.objects.filter(template_id=self.kwargs['id'], is_delete=False)


# Utility function
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
    ]

####
class FormDataReportViews(ActivityLogMixin,generics.ListAPIView):
    serializer_class = FormDataSerializer
    def get(self,request, *args, **kwargs):
        user_id=self.request.user.id
        startdate=self.request.query_params.get("startdate",None)
        print(startdate)
        if startdate != None:
            startdate=startdate+' '+"00:00:000"
          
        enddate=self.request.query_params.get("enddate",None)
        if enddate != None:
            enddate=enddate+' '+"23:59:000"
        user=self.request.query_params.get("user",None)
        template=self.request.query_params.get("template",None)
        where="WHERE public.forms_template.is_delete=false AND public.common_userpermissionsformdata.user_id="+ str(user_id) 
        if template != None:
            where=where + "AND public.common_userpermissionsformdata.template_id="+ str(template)
        c = connection.cursor()
        val="""SELECT distinct public.forms_template.label FROM public.common_userpermissionsformdata  inner Join public.forms_template on  public.common_userpermissionsformdata.template_id=public.forms_template.id """ + where
        val3=""
        with connection.cursor() as cursor:
            cursor.execute(val)
            row1 = cursor.fetchall()
            cnt=0
            for i in row1:
                if cnt == 0:
                   val3=val3 +'"'+i[0] +'" bigint'
                   cnt=1
                else:
                  val3=val3 +', "'+i[0] +'" bigint'
                  cnt=1 
        where1="WHERE public.forms_formdata.is_delete=false"
        if startdate and enddate:
            where1 = f"{where1} AND public.forms_formdata.date_added BETWEEN '{startdate}' AND '{enddate}'"
        if user !=None:
            where1=where1 +" AND public.forms_formdata.user_id="+ str(user)

        val2="""SELECT * FROM crosstab( $$select Max(public.users_user.email), Max(public.forms_template.label),Count(public.forms_formdata.id) qty FROM public.forms_formdata inner Join public.forms_template on public.forms_formdata.template_id=public.forms_template.id inner join public.users_user on public.forms_formdata.user_id=public.users_user.id """+where1+""" GROUP BY public.forms_formdata.template_id,public.users_user.email ORDER BY 1,2 $$,$$ SELECT distinct public.forms_template.label FROM public.common_userpermissionsformdata  inner Join public.forms_template on  public.common_userpermissionsformdata.template_id=public.forms_template.id """ + where +""" $$) AS ct ("User" text,""" + val3 + """)"""
        with connection.cursor() as cursor:
            cursor.execute(val2)
            rows = dictfetchall(cursor)

        return Response({'data':rows})


class FormDataListToeknView(ActivityLogMixin,generics.ListAPIView):
    serializer_class = FormDataSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class=None

    def get_queryset(self):
        share_form = get_object_or_404(klass=ShareForm,  token=self.kwargs['token'],
                                        is_delete=False,permission ='ANYONE_WITH_LINK' )

        if share_form:
            fields_data=Fields.objects.filter(template_id=share_form.template.id,is_delete=False , master_data_code=self.kwargs['id'])
            if fields_data:
                return FormData.objects.filter(template_id=self.kwargs['id'],is_delete=False)
            else:
                return()

        return()
    
    def get_log_message(self, request) -> str:
        return f"{request.user} is reading all users"  


class TemplateFieldStyleView(ActivityLogMixin,generics.ListCreateAPIView):
    serializer_class = TemplateFieldStyleSerializer
    queryset = TemplateFieldStyle.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    
   
class TemplateFieldStyleUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TemplateFieldStyleSerializer
    queryset = TemplateFieldStyle.objects.all()
    lookup_field = 'id'


class UpdateFields(APIView):
   serializer_class = FieldsSerializer
   def put(self,request):
        # Get the data to update from the request body
        data = request.data
        # Loop through the data and update the corresponding objects
        list1=[]
        for item in data:
            # Get the object by ID
            obj_id = item.get('id')
            obj = Fields.objects.filter(id=obj_id).first()


            if obj:
                # Update the object with the new data
                serializer = FieldsSerializer(obj, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    list1.append(serializer.data)

                
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(list1)



class FormDataAdvancedSearchView(generics.ListAPIView):
    serializer_class=FormDataSerializer

    def get(self,request, *args, **kwargs):
        # queryset=Data.objects.all()
        template_ocr=Template.objects.get(id=self.kwargs['id'])
        queryset1=FormData.objects.filter(template_id=self.kwargs['id']).filter(is_delete=False)
        value=request.query_params.get("value",None)
        if value:
            queryset1=queryset1.filter(data__value__icontains=value)
            # data=Response(FormData.objects.filter(template_id=self.kwargs['id']).filter(is_delete=False).filter(Q(data__field_id=field_id)&Q(data__value__icontains=value)))
            queryset1= FormDataSerializer(queryset1,many=True)
            return Response(queryset1.data)
            
        else:
            data=queryset1
            data= FormDataSerializer(data,many=True)
            return Response(data.data)        