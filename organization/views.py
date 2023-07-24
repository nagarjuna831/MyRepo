from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from rest_framework import generics, viewsets,status
from .serializers import *
from .models import *
from .permissions import * 
from rest_framework.response import Response

class OrganizationListCreateView(generics.ListCreateAPIView):
    parser_class = (FileUploadParser, MultiPartParser, FormParser, JSONParser)
    serializer_class = OrganizationSerializers
    queryset = Organization.objects.filter(is_delete=False)

    def create(self, request, *args,**kwargs):
        billing= get_object_or_404(klass=Billing,user=request.user.id)
        billing_accont=billing.active
        if billing_accont == "YES":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:    
            return Response({"message":"create your billing account"})


class OrganizationRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializers
    queryset = Organization.objects.filter(is_delete=False)
    lookup_field = 'id'


class MemberCreateView(generics.CreateAPIView):
    serializer_class = MembersSerializers
    queryset = Members.objects.filter(is_delete=False)


class OrganizationMemberListView(generics.ListAPIView):
    serializer_class = MembersSerializers

    def get_queryset(self):
        return Members.objects.filter(organization_id=self.kwargs['id'])


class OrganizationCheckView(generics.ListAPIView):
    serializer_class = OrganizationSerializers

    def get_queryset(self):
        return Organization.objects.filter(panel_access_url=self.kwargs['public_url'])
