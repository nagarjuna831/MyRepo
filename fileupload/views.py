from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import generics, status, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from rest_framework.response import Response
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from fileupload.models import Files
from fileupload.serializers import FileSerializer, FileSerializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filters import FileFilter
from datetime import datetime
from forms.models import ShareForm
from django.conf import settings

media_root = settings.MEDIA_ROOT
from subscription.models import Billing


def get_directory_size(path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size


class FilesCreateGetApiViews(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    parser_class = (FileUploadParser, MultiPartParser, FormParser, JSONParser)
    serializer_class = FileSerializer
    queryset = Files.objects.filter(is_delete=False)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_class = FileFilter
    ordering_fields = ('date_added', 'file')
    ordering = ('-id',)
    search_fields = ('file', 'name', 'type')

    def perform_create(self, serializer):
        billings = Billing.objects.get(user=self.request.user)
        data_assign = billings.space_assign
        data = get_directory_size(media_root + "/" + billings.billing_name)
        datas = data / 1048576
        data_assign = int(data_assign.split()[0])
        print(datas, data_assign)
        print(media_root + "/" + billings.billing_name)
        if data_assign > datas:
            serializer.save()
        else:
            return ()

    def get_queryset(self):
        user = self.request.user
        return Files.objects.filter(is_delete=False, user=user)


class FileUpdateApiViews(generics.RetrieveUpdateDestroyAPIView):
    parser_class = (FileUploadParser, MultiPartParser, FormParser, JSONParser)
    serializer_class = FileSerializer
    queryset = Files.objects.filter(is_delete=False)
    lookup_field = 'id'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Files.objects.filter(id=self.kwargs['id']).filter(is_delete=False)


class FileDownloadViews(generics.GenericAPIView):
    serializer_class = FileSerializer

    def get(self, request, id=None, format=None):
        try:
            files = get_object_or_404(
                klass=Files, id=id
            )
            file = files.file.path
            type = file.split('.')[-1].lower()
            document = open(file, 'rb')
            response = HttpResponse(FileWrapper(document), content_type='application/{}'.format(type))
            response['Content-Disposition'] = 'attachment;filename="%s"' % files.file.name
            return response
        except ValidationError:
            return Response({"detail": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)
        except FileNotFoundError:
            return Response({"detail": "Document not available"}, status=status.HTTP_404_NOT_FOUND)


class FileSharedDataViews(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FileSerializer
    lookup_field = 'id'

    def get_queryset(self):
        today = str(datetime.now())
        share_form = get_object_or_404(klass=ShareForm, token=self.kwargs['token'], is_delete=False)

        if share_form:
            return Files.objects.filter(id=self.kwargs['id'], is_delete=False)
        else:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class PostSharedFileData(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FileSerializer

    def post(self, request, *args, **kwargs):
        today = str(datetime.now())
        share_form = get_object_or_404(klass=ShareForm, scope='ADD', token=self.kwargs['token'], is_delete=False)
        if share_form:
            serializer = FileSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "file data saved successful", "data": serializer.data},
                                status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class FileDownloadsViews(generics.GenericAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, id=None, format=None, token=None):
        today = str(datetime.now())
        share_form = get_object_or_404(klass=ShareForm, scope='VIEW', token=self.kwargs['token'], is_delete=False)
        if share_form:
            try:
                files = get_object_or_404(
                    klass=Files, id=id
                )
                file = files.file.path
                type = file.split('.')[-1].lower()
                document = open(file, 'rb')
                response = HttpResponse(FileWrapper(document), content_type='application/{}'.format(type))
                response['Content-Disposition'] = 'attachment;filename="%s"' % files.file.name
                return response
            except ValidationError:
                return Response({"detail": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)
            except FileNotFoundError:
                return Response({"detail": "Document not available"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import os


class MediaStorageSizeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Get the size of the media storage
        media_path = os.path.join(settings.MEDIA_ROOT, '')
        media_size = sum(os.path.getsize(os.path.join(media_path, f)) for f in os.listdir(media_path) if
                         os.path.isfile(os.path.join(media_path, f)))

        # Convert the size to a human-readable format
        media_size_kb = media_size / 1024
        media_size_mb = media_size_kb / 1024
        media_size_gb = media_size_mb / 1024

        # Return the response
        return Response({
            "media_size": {
                "bytes": media_size,
                "kilobytes": media_size_kb,
                "megabytes": media_size_mb,
                "gigabytes": media_size_gb,
            }
        })


import io
import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path
from PyPDF2 import PdfFileReader
from io import BytesIO
import PyPDF2
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from pdf2image import convert_from_bytes

import io
import PIL.Image
import pyocr
import pyocr.builders
from django.http import JsonResponse
from rest_framework import views, status


class FilesOcrApiViews(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            pdf = serializer.save()
            print(pdf.file.name)
            print(request.data['file'])
            pdf_path = os.path.join(settings.MEDIA_ROOT, pdf.file.name)
            images = convert_from_path(pdf_path)
            text = ''
            for image in images:
                text += pytesseract.image_to_string(image)

            # response = HttpResponse(text, content_type='text/plain')
            # response['Content-Disposition'] = f'attachment; filename="{pdf.file.name}.txt"'
            # response['X-Response-ID'] = serializer.data['id']
            return Response({"id": serializer.data['id'], "text": text})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
