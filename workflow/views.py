from rest_framework import viewsets, generics,status
from .serializers import *
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filters import WorkflowFilter, StateFilter
import json
from forms .models import FormData ,Template
from forms .serializers  import FormDataSerializer ,TemplateSerializer
from rest_framework.response import Response
from users .models import User
from django.db import connection
from django.shortcuts import get_object_or_404
from .permisssions import WorkflowPermission
from subscription.models import Billing
from subscription.serializers import BillingSerializer
import ast 


class WorkflowListCreate(generics.ListCreateAPIView):
    serializer_class = WorkflowSerializer
    queryset = Workflow.objects.filter(is_delete=False)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = WorkflowFilter
    ordering_fields = ('date_added', 'label')
    ordering = ('-id',)
    search_fields = ('label', 'date_added', 'date_updated', 'description')
    
    
    def create(self, request, *args,**kwargs):
        billing= Billing.objects.filter(user=request.user.id)
        if billing:
            billing= BillingSerializer(billing,many=True)
            billing=billing.data
            billing=json.loads(json.dumps(billing))
            billing_accont=billing[0]['active']
            workflow_count=billing[0]['workflow_count']

            if billing_accont == "YES":
                workflows_count=Workflow.objects.filter(user=request.user.id).filter(is_delete=False ).count()
                if workflow_count >= workflows_count+1: 
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message":" your billing account have not permission to create workflow"},status=status.HTTP_400_BAD_REQUEST)

            else:    
                return Response({"message":" your billing account is not active"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"create your billing account"},status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self): 
        user = self.request.user
        return Workflow.objects.filter(user=user).filter(is_delete=False )
    

class WorkflowListView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkflowSerializer
    queryset = Workflow.objects.filter(is_delete=False)
    lookup_field = 'id'


class StateListView(generics.ListAPIView):
    serializer_class = StateSerializer

    def get_queryset(self):
        return State.objects.filter(workflow=self.kwargs['id'], is_delete=False)


class StateViewSet(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.filter(is_delete=False)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = StateFilter
    ordering_fields = ('date_added', 'workflow')
    ordering = ('date_added',)
    search_fields = ('date_added', 'date_updated', 'workflow')


class StateTransitionListView(generics.ListAPIView):
    serializer_class = TransitionSerializer

    def get_queryset(self):
        return Transition.objects.filter(origin_state=self.kwargs['id'])


class TransitionViewSet(viewsets.ModelViewSet):
    serializer_class = TransitionSerializer
    queryset = Transition.objects.filter(is_delete=False)


class TransitionWorkflowView(generics.ListAPIView):
    serializer_class = TransitionSerializer

    def get_queryset(self):
        return Transition.objects.filter(workflow=self.kwargs['workflow_id'])  


class TemplateWorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateWorkflowSerializer
    queryset = TemplateWorkflow.objects.all()


class WorkflowActionView(generics.CreateAPIView):
    serializer_class = WorkflowInstanceLogCreateSerializer
    queryset = WorkflowInstanceLog.objects.all()


class WorkflowInstanceLogView(generics.ListAPIView):
    serializer_class = WorkflowInstanceLogSerializer

    def get_queryset(self):
        return WorkflowInstanceLog.objects.filter(form_data__id=self.kwargs['id'])


class WorkflowInstanceLogViews(generics.ListCreateAPIView):
    serializer_class = WorkflowInstanceSerializer
    queryset =WorkflowInstance.objects.all()

    def get_queryset(self):
        try:
            user = self.request.user
            member = WorkflowStateMember.objects.filter(user=user,is_delete=False)
            member = WorkflowTemplatetatesSerializer(member , many=True)
            data=json.loads(json.dumps(member.data))
            datalist=[]
            for i in data:
                data=WorkflowInstance.objects.filter(current_state=i['state'])
                if data:
                    data=WorkflowInstanceSerializer(data, many=True)
                    count += data.count()
                    
                else:
                    pass
            
            
            return WorkflowInstance.objects.filter(current_state=i['state'])       
        except:
            return WorkflowInstance.objects.filter(user=user)


# Utility function
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
    ]

####

class WorkflowTemplateStateViews(generics.ListCreateAPIView):
    serializer_class = WorkflowTemplatetatesSerializer
    queryset = WorkflowStateMember.objects.filter(is_delete=False)

    def post(self, request, *args, **kwargs):
        c = connection.cursor()
        data=self.request.body.decode()
        data=ast.literal_eval(data)
        user=data['user']
        template=data['template']
        state_name=data['state_name']
        check_qery='''Select * from workflow_workflowstatemember WHERE  template_id='''+ str(template )+' AND user_id='''+ str(user )+''
        with connection.cursor() as cursor:
            cursor.execute(check_qery)
            rows = dictfetchall(cursor)
        
        if rows is None:
            with connection.cursor() as cursor:
                for i in state_name:
                    query = ''' INSERT INTO workflow_workflowstatemember (date_added,date_updated,is_delete,state_id,template_id,user_id)  VALUES (current_timestamp,current_timestamp,False,'''+ str(i) +',''' + str(template) + ''','''+ str(user) +''') '''
                    cursor.execute(query)   
                    

            return Response({'status':'ok'})         
        else:
            with connection.cursor() as cursor:
                print('yes')
                check_qery='''DELETE  from workflow_workflowstatemember WHERE template_id='''+ str(template )+' AND user_id='''+ str(user )+''
                cursor.execute(check_qery)    
                for i in state_name:
                    query = ''' INSERT INTO workflow_workflowstatemember (date_added,date_updated,is_delete,state_id,template_id,user_id)  VALUES (current_timestamp,current_timestamp,False,'''+ str(i) +' ,''' + str(template) + ''','''+ str(user) +''') '''
                    cursor.execute(query)    
                    
            return Response({'status':'ok'})


class WorkflowStateMemberViews(generics.ListAPIView):
    serializer_class = WorkflowTemplatetatesSerializer

    def get_queryset(self):
        return WorkflowStateMember.objects.filter(template_id=self.kwargs['template_id'],user_id=self.kwargs['user_id'],is_delete=False)