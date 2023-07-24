from .models import *
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from users.serializers import UsersSerializer
from commons.models import UserPermissionsFormdata
from subscription.serializers import BillingSerializer

class ValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validation
        fields = '__all__'


class FieldsSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True, required=False)
    validation = ValidationSerializer(required=False)

    class Meta:
        model = Fields
        fields = '__all__'

    def create(self, validated_data):
        validation = validated_data.pop('validation', None)
        validated_data['user'] = self.context['request'].user
        if validation is not None:
            validation = Validation.objects.create(**validation)
        field = Fields.objects.create(**validated_data, validation=validation)
        return field

    def update(self, instance, validated_data):
        validation = validated_data.pop('validation', None)
        instance_validation = instance.validation
        if instance_validation is None:
            new_validation = Validation.objects.create(**validation)
            instance.validation = new_validation
        else:
            if validation is not None:
                instance_validation.type = validation.get('type', instance_validation.type)
                instance_validation.expression = validation.get('expression', instance_validation.expression)
                instance_validation.error_message = validation.get('error_message', instance_validation.error_message)
            else:
                instance.validation = validation
            instance_validation.save()

        instance.template = validated_data.get('template', instance.template)
        instance.label = validated_data.get('label', instance.label)
        instance.type = validated_data.get('type', instance.type)
        instance.placeholder = validated_data.get('placeholder', instance.placeholder)
        instance.tooltip = validated_data.get('tooltip', instance.tooltip)
        instance.mandatory = validated_data.get('mandatory', instance.mandatory)
        instance.sequence = validated_data.get('sequence', instance.sequence)
        instance.display_in_main_view = validated_data.get('display_in_main_view', instance.display_in_main_view)
        instance.master_data_code = validated_data.get('master_data_code', instance.master_data_code)
        instance.check_unique = validated_data.get('check_unique', instance.check_unique)
        instance.unique_type = validated_data.get('unique_type', instance.unique_type)
        instance.auto_sum = validated_data.get('auto_sum', instance.auto_sum)
        instance.deafult_value = validated_data.get('deafult_value', instance.deafult_value)
        instance.style = validated_data.get('style', instance.style)
        instance.api= validated_data.get('api', instance.api)
        instance.values = validated_data.get('values', instance.values)
        instance.table_data = validated_data.get('table_data',instance.table_data)
        instance.ocr_view = validated_data.get('ocr_view',instance.ocr_view)
        instance.save()
        return instance


class TemplateSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    data_count = serializers.SerializerMethodField()
    field_count = serializers.SerializerMethodField()
    

    class Meta:
        model = Template
        fields = '__all__'

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['billing'] =Billing.objects.get(user_id=self.context['request'].user)
        return Template.objects.create(**validated_data)

    def get_data_count(self, obj):
        return FormData.objects.filter(template=obj.id,is_delete=False,user=obj.user.id).count()

    def get_field_count(self, obj):
        return Fields.objects.filter(template=obj.id,is_delete=False).count()
    
    
    
class DataSerializer(serializers.ModelSerializer):
    field_data = serializers.SerializerMethodField()

    class Meta:
        model = Data
        fields = '__all__'

    def get_field_data(self, obj):
        return FieldsSerializer(obj.field).data

   
class FormDataSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    data = DataSerializer(many=True)
    user = UsersSerializer(read_only=True, required=False)
    class Meta:
        model = FormData
        fields = '__all__'

    def create(self, validated_data):
        datas = validated_data.pop('data')
        user = self.context['request'].user
        if not user.is_anonymous:
            validated_data['user'] = self.context['request'].user
        
        form_data = FormData.objects.create(**validated_data)
        data_list = []
        for data in datas:
            new_data = Data.objects.create(**data)
            data_list.append(new_data.id)
            form_data.data.set(data_list)
        return form_data


class ShareFormSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)

    class Meta:
        model = ShareForm
        fields = '__all__'

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return ShareForm.objects.create(**validated_data)


class SharedFormDataSerializer(serializers.ModelSerializer):
    template = TemplateSerializer(read_only=True)
    user = UsersSerializer(read_only=True)
    template_fields = serializers.SerializerMethodField()

    def get_template_fields(self, obj):
        fields = Fields.objects.filter(template=obj.template.id, is_delete=False)
        return FieldsSerializer(fields, many=True).data

    class Meta:
        model = ShareForm
        fields = '__all__'


class FormDataCommentSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    user = UsersSerializer(read_only=True, required=False)

    class Meta:
        model = FormDataComment
        fields = '__all__'        
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return FormDataComment.objects.create(**validated_data)
    

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        return instance     


class FormdataMemberSerializer(serializers.ModelSerializer):
    
    user = UsersSerializer(read_only=True)
    
    class Meta:
        model = UserPermissionsFormdata
        fields = ['id','user','level',]


class TemplateFieldStyleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TemplateFieldStyle
        fields = '__all__'
