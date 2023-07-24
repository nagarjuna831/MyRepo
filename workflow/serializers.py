from .models import *
from rest_framework import serializers
from users.serializers import UsersSerializer
from users .models import User
from forms .models import FormData ,Template
from forms .serializers  import FormDataSerializer ,TemplateSerializer
import json


class WorkflowSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    class Meta:
        model = Workflow
        fields = '__all__'

    def create(self, validated_data):
        validated_data['billing'] =Billing.objects.get(user_id=self.context['request'].user)
        validated_data['user'] = self.context['request'].user
        return Workflow.objects.create(**validated_data)    


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'
    
    def create(self, validated_data):
       workflow_id=validated_data['workflow']
       is_initial=validated_data['is_initial']
    #  workflow_id=Workflow.objects.get(id=workflow_id.id)
       data=State.objects.filter(workflow_id=workflow_id.id, is_initial=True ,is_delete=False )
       if data and is_initial == True :
        raise serializers.ValidationError({'status':"workflow with is_initial true already exists"})
       else:
        return State.objects.create(**validated_data)    


class TransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transition
        fields = '__all__'


class TemplateWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateWorkflow
        fields = '__all__'


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    user_name= serializers.SerializerMethodField()
    template_name = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowInstance
        fields = '__all__'
    

    def get_user_name(self, obj):
        users = User.objects.filter(id=obj.user.id)
        data=UsersSerializer(users, many=True).data
        user=json.loads(json.dumps(data))
        data=user[0]['email']
        return(data)
    

    def get_template_name(self, obj):
        form_data=FormData.objects.filter(template=obj.form_data.id, is_delete=False)
        data=FormDataSerializer(form_data,many=True).data
        data=json.loads(json.dumps(data))
        if data:
            data=data[0]['template']
            return(data)
        else:
            return(None)
        
    
    def get_state_name(self, obj):
        state=State.objects.filter(id=obj.current_state.id)
        data=StateSerializer(state,many=True).data
        data=json.loads(json.dumps(data))
        if data:
            data=data[0]['label']
            return(data)
        else:
            return(None)


class WorkflowInstanceLogSerializer(serializers.ModelSerializer):
    transition = TransitionSerializer(read_only=True)
    user = UsersSerializer(read_only=True)

    class Meta:
        model = WorkflowInstanceLog
        fields = '__all__'


class WorkflowInstanceLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowInstanceLog
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        print(validated_data)
        validated_data['user'] = self.context['request'].user
        return WorkflowInstanceLog.objects.create(**validated_data)



class WorkflowTemplatetatesSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = WorkflowStateMember
        fields = '__all__'
   