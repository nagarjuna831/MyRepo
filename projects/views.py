from urllib import response
from rest_framework import viewsets, generics
from users.models import User
from users.serializers import UsersSerializer
from .serializers import ProjectSerializer
from .models import Project
from .filters import ProjectFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from forms.serializers import TemplateSerializer
from forms.models import Template
from commons.models import UserPermissionsTemplate
from commons.serializers import UserPermissionsTemplateSerializer
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from .permissions import *

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


class ProjectListViewSet(viewsets.ModelViewSet):
    permission_classes=[ProjectPermission,]
    pagination_class=OneByOneItems
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(is_delete=False)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = ProjectFilter
    ordering_fields = ('date_added', 'name')
    ordering = ('-id',)
    search_fields = ('name', 'description')

    def list(self, request, *args, **kwargs):
        self.pagination_class=OneByOneItems
        user = self.request.user
        data=UserPermissionsTemplate.objects.filter(user_id=self.request.user.id )
        page=self.request.query_params.get("page",None)
        if page == None:
            datas=Project.objects.all().filter(is_delete=False).filter(user=user)
            counts=Project.objects.all().filter(is_delete=False,user=self.request.user.id).count()
            newdata1=ProjectSerializer(datas,many=True)
            newdata4=newdata1.data
            newdata3=json.loads(json.dumps(newdata4))
            return Response({'count':counts,'data':newdata3})

        if data:
            templatepermission1=UserPermissionsTemplateSerializer(data,many=True)
            templatepermission2=templatepermission1.data    
            templatepermission3=json.loads(json.dumps(templatepermission2))
            data=templatepermission3
            data_list=[]
            count=0
            for i in data: 
                newdata=Project.objects.filter(id=i['project']).filter(is_delete=False)
                newdata1=ProjectSerializer(newdata,many=True)
                newdata4=newdata1.data
                newdata3=json.loads(json.dumps(newdata4))
                data_list.extend(newdata3)
                count += 1
            pages = self.paginate_queryset(data_list[::-1])
            return Response({'count':count,'data':pages})
        
        data=Project.objects.filter(user=user).filter(is_delete=False)
        count=data.count()
        newdata1=ProjectSerializer(data,many=True)
        newdata4=newdata1.data
        newdata3=json.loads(json.dumps(newdata4))
        pages = self.paginate_queryset(newdata3[::-1])
        return Response({'count':count,'data':pages})


class ProjectTemplateListView(generics.ListAPIView):
    serializer_class = TemplateSerializer

    def get_queryset(self):
        return Template.objects.filter(project_id=self.kwargs['id']).filter(is_delete=False)


class ProjectOrganizationListView(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(organization_id=self.kwargs['id']).filter(is_delete=False)


class ProjectUserListView(APIView):
    def get(self,request,id=None):
        Data=UserPermissionsTemplate.objects.filter(project_id=id)
        userlist=[]
        for i in Data:
            data2=User.objects.filter(id=i.user.id)
            data3=UsersSerializer(data2,many=True)
            data4=data3.data
            userdata=json.loads(json.dumps(data4))
            datalist=({'id':i.id,'user':userdata[0],'level':i.level})
            userlist.append(datalist)
        return Response(userlist)          