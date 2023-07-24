from rest_framework import serializers
from .models import *
from users.serializers import UsersSerializer
from forms.serializers import TemplateSerializer
from forms.models import Template 
import json 
from users.models import User


class DefaultValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultValue 
        fields = '__all__'
 

class UserPermissionsSerializer(serializers.ModelSerializer):

    deafult_value = DefaultValueSerializer(many=True)
    class Meta:
        model =  UserPermissionsFormdata
        fields = "__all__"
    

    def create(self, validated_data):
        deafult_value = validated_data.pop('deafult_value')
        form_data = UserPermissionsFormdata.objects.create(**validated_data)
        data_list = []
        for data in deafult_value:
            new_data = DefaultValue.objects.create(**data)
            data_list.append(new_data.id)
            form_data.deafult_value.set(data_list)
        return form_data
    
class UserPermissionUpdatesSerializer(serializers.ModelSerializer):

    deafult_value = DefaultValueSerializer(many=True ,read_only=True)
    class Meta:
        model =  UserPermissionsFormdata
        fields = "__all__"
    

    def create(self, validated_data):
        deafult_value = validated_data.pop('deafult_value')
        form_data = UserPermissionsFormdata.objects.create(**validated_data)
        data_list = []
        for data in deafult_value:
            new_data = DefaultValue.objects.create(**data)
            data_list.append(new_data.id)
            form_data.deafult_value.set(data_list)
        return form_data    

    
class UserPermissionsTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model =  UserPermissionsTemplate
        fields = "__all__"


class UserPermissionsFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model =  UserPermissionsFields
        fields = "__all__"  


class TeamSerializer(serializers.ModelSerializer):
    user =  UsersSerializer(read_only=True)
    class Meta:
        model =  Team
        fields = "__all__"  
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return  Team.objects.create(**validated_data)


class TeamUsersSerializer(serializers.ModelSerializer):
    template=serializers.SerializerMethodField()
    class Meta:
        model =  Team
        fields = "__all__"
    
    def get_template(self, obj):
        fields =Template.objects.filter(id=obj.template.id)
        data=TemplateSerializer(fields,many=True).data
        data=json.loads(json.dumps(data))

        if data:
            template=data[0]['label']
            if template:
                return template
            else:
                return ""    
        
        return ''


class TeamTemplateSerializer(serializers.ModelSerializer):
    template = serializers.SerializerMethodField()
    class Meta:
        model =  Team
        fields = "__all__"

    def get_template(self, obj):
        fields =Template.objects.filter(id=obj.template_id)
        data=TemplateSerializer(fields,many=True).data
        data=json.loads(json.dumps(data))
        if data:
            template=data[0]['label']
            if template:
                return template
            else:
                return ""    
        
        return ''


class TeamPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model =  TeamPermission
        fields = "__all__"  


class TeamsUserSerializer(serializers.ModelSerializer):
    team= serializers.SerializerMethodField()
    class Meta:
        model =  TeamPermission
        fields = ['team']
    

    def get_team(self, obj):
        team =Team.objects.filter(id=obj.team.id)
        data=TeamSerializer(team,many=True).data
        data1=json.loads(json.dumps(data))
        template=(data1[0]['template'])
        fields =Template.objects.filter(id=template)
        data=TemplateSerializer(fields,many=True).data
        data=json.loads(json.dumps(data))
        template=data[0]['label']
        id=data1[0]['id']
        name=data1[0]['name']
        return {'id':id,'name':name,'template':template}


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    class Meta:
        model =  TeamPermission
        fields = ['id' ,'user','team_lead']


class TeamTemplateMemberSerializer(serializers.ModelSerializer):
    userdata = serializers.SerializerMethodField()

    def get_userdata(self, obj):
        fields =TeamPermission.objects.filter(team_id=obj.id ,team_lead=1)
        data=TeamPermissionSerializer(fields,many=True).data
        data=json.loads(json.dumps(data))
        print(data)
        if  data:
            user=data[0]['user']
            if user:
                data=User.objects.filter(id=user)
                data=UsersSerializer(data,many=True).data
                data=json.loads(json.dumps(data))
                print(data)
                return data[0]
            

    class Meta:
        model = Team
        fields = ['userdata','name']  


class ConfigurationSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model =  ConfigurationSettings
        fields = "__all__"  


class TeamLeadSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()
    class Meta:
        model =  TeamPermission
        fields =('id','team','team_name')
    
    def get_team_name(self, obj):
        fields =Team.objects.filter(id=obj.team.id)
        data=TeamSerializer(fields,many=True).data
        data=json.loads(json.dumps(data))
        return data[0]['name']


class TeamUserSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model =  TeamPermission
        fields =('user',)
    
    def get_user(self, obj):
        fields =User.objects.filter(id=obj.user.id)
        data=UsersSerializer(fields,many=True).data
        data=json.loads(json.dumps(data))
        return data[0]


class NotificationSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    class Meta:
        model =  Notification
        fields ="__all__"

class CustomFormSerializer(serializers.ModelSerializer):
    # user= UsersSerializer(read_only=True)
    class Meta :
        model= CustomForm
        fields = "__all__"