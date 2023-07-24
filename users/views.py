from ast import Delete
from rest_framework import generics, viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from .models import User
from .serializers import UsersSerializer, UserChangePasswordSerializer, UsersUpdateSerializer, LogoutSerializer, ResetPasswordEmailRequestSerializer ,SetNewPasswordSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from .filters import UserFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
import os
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from systemlog.utility import ActivityLogMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings


class UserCreateView(ActivityLogMixin, generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UsersSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email=serializer.data['email']
        user=User.objects.get(email=email)
        token=RefreshToken.for_user(user)
        # current_site=get_current_site(request).domain
        # relativelink=reverse('email_verify')
        redirect_url = self.request.query_params.get('redirect_url', '')
        absurl = redirect_url+"?token="+str(token)
        # email_body='Hi use link below to verify your email \n'+absurl
        # print(email_body)
        context={'username': email,
                  'link'   :absurl,
                }
        html_message = render_to_string('userwelcome.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail('Welcome to Epsumlabs',plain_message, 'eform@epsumlabs.in', [email], html_message=html_message)       
        return Response(serializer.data,status=status.HTTP_200_OK)



class VerifyEmail(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self,request):
        token=request.GET.get('token')
        try:
            payload=jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
            user=User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'email':'Successfully activated'},status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:

            return Response({'error':'Activation Expired'},status=status.HTTP_400_BAD_REQUEST) 
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'invalid token'},status=status.HTTP_400_BAD_REQUEST) 



class AllUserListView(ActivityLogMixin, generics.ListAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = UserFilter
    ordering_fields = ('is_superuser', 'name')
    ordering = ('name',)
    search_fields = ('name', 'email', 'phone', 'is_superuser')

    def get_log_message(self, request) -> str:
        return f"{request.user} is reading all users"



class ChangePasswordView(ActivityLogMixin, generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = UserChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            email=self.object
            context={'UserName': email,
                    'message': 'your Password  has been updated successfully'}
            html_message = render_to_string('passwordchange.html', context)
            plain_message = strip_tags(html_message)
            send_mail('Welcome to Epsumlabs',html_message, 'eform@epsumlabs.in', [email], html_message=html_message) 
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def get_log_message(self, request) -> str:
        return f" Password updated successfully"



class UserUpdateViews(ActivityLogMixin, generics.GenericAPIView):
    parser_class = (FileUploadParser, MultiPartParser, FormParser, JSONParser)
    serializer_class = UsersUpdateSerializer
    queryset = User.objects.all()

    def get(self,request, *args, **kwargs):
        id = self.request.user.id
        user = User.objects.get(id=id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def put(self, request, id=None):
        id = self.request.user.id
        user = User.objects.get(id=id)
        serializer = UsersUpdateSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'msg': "Profile Updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get_log_message(self, request) -> str:
        if request.method == 'GET':
            return f" get user successfully"
        if request.method == 'PUT':
            return f" Profile Updated successfully"



class UserProfileUpdateViews(ActivityLogMixin, generics.GenericAPIView):
    parser_class = (FileUploadParser, MultiPartParser, FormParser, JSONParser)
    serializer_class = UsersUpdateSerializer
    queryset = User.objects.all()

    def put(self, request, id=None):
        user = User.objects.get(id=id)
        serializer = UsersUpdateSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'msg': "Profile Updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_log_message(self, request) -> str:
        return f" Profile updated successfully"


class LogoutAPIView(ActivityLogMixin, generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteAPIView(ActivityLogMixin, generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request,id=None):
        user = User.objects.get(id=id)
        user.delete()
        return Response({'msg': "User Deleted successfully"},status=status.HTTP_200_OK)

    def get_log_message(self, request) -> str:
        return f" User deleted  successfully"    



class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RequestPasswordResetEmail(ActivityLogMixin, generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')
       

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = current_site + relativeLink
            email_body = absurl+"?redirect_url="+redirect_url
           
            email=user.email
            context={'UserName': email,
                    'link': email_body}
            html_message = render_to_string('forgetpasswords.html', context)
            plain_message = strip_tags(html_message)
            send_mail('Welcome to Epsumlabs',plain_message, 'eform@epsumlabs.in', [email], html_message=html_message)     
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
            
        return Response({'success': 'You are not a valid User'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(ActivityLogMixin, generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)



class SetNewPasswordAPIView(ActivityLogMixin, generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.AllowAny] 

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)