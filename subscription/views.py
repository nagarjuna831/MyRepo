from django.shortcuts import render
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
import json
from rest_framework.views import APIView
from users.models import User
from users.serializers import UsersSerializer
from rest_framework import generics, status, permissions, status
from forms.models import Template        
from commons.models import Team
from workflow.models import Workflow
import os                
from django.conf import settings

import time   
import environ
from datetime import  timedelta
from .payment_sdk.paytring_sdk import *      
from django.db import IntegrityError 
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
media_root = settings.MEDIA_ROOT

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


def place_order(data, amount:int, callback_url:str):
    customer_info = {
        'email': data['email'],
        'phone': data['contact_no'],
        'cname': data['billing_name']
    }
    receipt_id = str(int(time.time())) + str(data['id'])
    # amount = str(amount * 100)
    amount = str(amount)
    order_obj = Order()
    order_res = order_obj.Create(receipt_id, amount, callback_url, customer_info)
    return order_res['response']
# Create your views here.


class BilingListViewSet(viewsets.ModelViewSet):
    
    serializer_class = BillingSerializer
    queryset = Billing.objects.all()

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            real_subscrip_type = data['subscription_type']
            real_duration = data['duration']
            order_amount = 0

            if real_duration == 30:
                order_amount = SubscriptionModel.objects.get(name=real_subscrip_type).monthly_amount
            elif real_duration == 365: 
                order_amount = SubscriptionModel.objects.get(name=real_subscrip_type).yearly_amount   
            else:
                raise ValueError
            subscription = SubscriptionModel.objects.get(name = 'Free')
            subscrip_serializer = SubscriptionSerializer(subscription)
            data['duration'] = 30
            data['form_count'] = subscrip_serializer.data['form_count']
            data['team_count'] = subscrip_serializer.data['team_count']
            data['workflow_count'] = subscrip_serializer.data['workflow_count']
            data['email_count'] = subscrip_serializer.data['email_count']
            data['custome_form_count'] = subscrip_serializer.data['custome_form_count']
            data['e_signature_count'] = subscrip_serializer.data['e_signature_count']
            data['space_assign'] = subscrip_serializer.data['space_assign']
            data['monthly_submission'] = subscrip_serializer.data['monthly_submission']
            data['subscription_type'] = 'Free'
            billing_serializer = BillingSerializer(data=data)
            if billing_serializer.is_valid():
                self.perform_create(billing_serializer)
                billing_serializer.save()
            else:
                return Response({
                    'success': False,
                    'errors': billing_serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if real_subscrip_type == 'Free':
                free_data = {}
                free_data.update(billing_serializer.data)
                free_data.update({'url': ""})
                return Response({
                    'success': True,
                    'data': free_data,
                    'message': 'Billing account is successfully created'
                }, status.HTTP_201_CREATED)
            
            # place the order 
            callback_url = request.build_absolute_uri('/') + 'billings/fetch-order/'
            create_order_data = place_order(billing_serializer.data, order_amount, callback_url)
            order_data = {
                'hash_id': create_order_data['hash'],
                'order_id': create_order_data['order_id'],
                'billing': billing_serializer.data['id'],
                'subscription_type': real_subscrip_type,
                'duration': real_duration,
                'amount': order_amount
            }
            payment_serializer = BillingPaymentSerializer(data=order_data)
            if payment_serializer.is_valid():
                payment_serializer.save()
                data = {}
                data.update({'url':create_order_data['url'] })
                data.update(billing_serializer.data)
                return Response({
                    'success': True,
                    'data': data,
                    'message': 'Billing account is successfully created!'
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'data': payment_serializer.errors
                },status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'success': False,'error': 'Invalid Data'}, status.HTTP_400_BAD_REQUEST) 
        except IntegrityError :
            return Response({
                'success': False,
                'error': 'Billing account is already exit !'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                'success': False,
                'errors': 'Something went wrong'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



class  BilingListUserViewSet(APIView):
    def get(self,request,id=None):  
        user=self.request.user.id
        Datas=Billing.objects.filter(user=user)
        if Datas:
            datas=BillingSerializer(Datas,many=True)
            datas=datas.data
            return Response(datas[0])
        else:
            data2=User.objects.filter(id=user)
            data3=UsersSerializer(data2,many=True)
            data4=data3.data

            return Response( {"user":data4[0],
                            "billing_name": "",
                            "contact_no": "",
                            "email": "",
                            "gst_no": "",
                            "date_added": "",
                            "active": "",
                            "subscription_type": "",
                            })
        


def get_directory_size(path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size


class  BilingSubscriptionView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self,request,id=None):  
        try:
            user=self.request.user.id
            Datas=Billing.objects.get(user=user)
            forms=Template.objects.filter(user=user,is_delete=False).count()
            teams=Team.objects.filter(user=user).count()
            workflow=Workflow.objects.filter(user=user).count()
            data_assign= Datas.billing_name
            data=get_directory_size(media_root+"/"+data_assign)
            datas=data/1048576
            # data_assign=int(data_assign.split()[0])
            list1=[]
            list1.extend([{"name":"forms","total":Datas.form_count ,"uses":forms},{"name":"team","total":Datas.team_count,"uses":teams},{"name":"workflow","total":Datas.workflow_count,"uses":workflow},{"name":"space","total":Datas.space_assign+'MB',"uses":str(datas)+'MB'},{"name":"email","total":Datas.email_count,"uses":""},{"name":"custome_form","total":Datas.custome_form_count,"uses":""},{"name":"e_signature","total":Datas.e_signature_count,"uses":""}])
            return Response (list1)
        except Billing.DoesNotExist:
            data = []
            return Response(data, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': 'Something went wrong!'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class  FetchPaymentView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        try:
            order_id = request.data['order_id']

            # fetch order status from paytring
            order_obj = Order()
            response = order_obj.Fetch(order_id)['response']
            # print(response)
            
            order_status = response['order']['order_status']
            payment_id = response['order']['pg_transaction_id']
            billing_payment = BillingPayment.objects.filter(order_id=order_id).first()
            billing_payment.payment_id = payment_id
            billing_payment.payment_status = order_status
            billing_payment.save()

            if order_status == 'success':
                billing = Billing.objects.filter(id = billing_payment.billing.id).first()
                subscription = SubscriptionModel.objects.filter(name=billing_payment.subscription_type).first()
                billing.form_count = subscription.form_count
                billing.team_count = subscription.team_count
                billing.workflow_count = subscription.workflow_count
                billing.email_count = subscription.email_count
                billing.custome_form_count = subscription.custome_form_count
                billing.e_signature_count = subscription.e_signature_count
                billing.space_assign = subscription.space_assign
                billing.monthly_submission = subscription.monthly_submission
                billing.payment_done = 'Y'
                billing.duration = billing_payment.duration
                billing.subscription_type = billing_payment.subscription_type
                billing.expiry_date = billing.expiry_date + timedelta(days=billing_payment.duration)
                billing.save()
                success_url  = env('PAYMENT_SUCCESS_URL')

                # print(success_url)
                return redirect(success_url)
                # return Response({'status': order_status})
            else:
                fail_url = env('PAYMENT_FAIL_URL')
                # print(fail_url)
                return redirect(fail_url)
                # return Response({'status': order_status})
            
        except ObjectDoesNotExist :
            return Response({
                'status':False,
                'message': 'The billing payment is not exit !'
            }, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                'status':False,
                'message': 'Something went wrong!'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreatePaymentView(generics.CreateAPIView):
    serializer_class = BillingPaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            print(data)
            real_subscrip_type = data['subscription_type']
            real_duration = data['duration']
            order_amount = 0

            if real_duration == 30:
                order_amount = SubscriptionModel.objects.get(name=real_subscrip_type).monthly_amount
            elif real_duration == 365: 
                order_amount = SubscriptionModel.objects.get(name=real_subscrip_type).yearly_amount   
            else:
                raise ValueError
            billing= Billing.objects.get(id=data['billing'])
            billing_serializer = BillingSerializer(billing)
            callback_url = request.build_absolute_uri('/') + 'billings/fetch-order/'
            create_order_data = place_order(billing_serializer.data, order_amount, callback_url)
            order_data = {
                'hash_id': create_order_data['hash'],
                'order_id': create_order_data['order_id'],
                'billing': billing_serializer.data['id'],
                'subscription_type': real_subscrip_type,
                'duration': real_duration,
                'amount': order_amount
            }
            payment_serializer = BillingPaymentSerializer(data=order_data)
            if payment_serializer.is_valid():
                payment_serializer.save()
                data = {}
                data.update({'url':create_order_data['url'] })
                data.update(billing_serializer.data)
                return Response({
                    'success': True,
                    'data': data,
                    'message': 'Billing account is successfully created!'
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'data': payment_serializer.errors
                },status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'success': False,'error': 'Invalid Data'}, status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            print(e)
            return Response({
                'success': False,
                'error': 'Something went wrong !'
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)
