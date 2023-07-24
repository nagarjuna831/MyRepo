from rest_framework import generics, status
from rest_framework.response import Response
from users.models import User
from forms.models import Template, FormData
from fileupload.models import Files
from workflow.models import Workflow
from projects.models import Project
from .serializers import *
from commons.models import *
from commons.serializers import *
import json
from users.serializers import UsersSerializer


class DashboardStatsViews(generics.ListAPIView):
    serializer_class = StatsSerializer

    def get(self, request):
        # form_count=0
        # data=UserPermissionsFormdata.objects.filter(user_id=self.request.user.id )
        # # if data:
        #     templatepermission1=UserPermissionsSerializer(data,many=True)
        #     templatepermission2=templatepermission1.data
        #     templatepermission3=json.loads(json.dumps(templatepermission2))
        #     data=templatepermission3
        #     if data:
        #         for i in data: 
        #             newdata=Template.objects.filter(id=i['template']).filter(is_delete=False)
        #             form_count += 1

        # else:
        #     form_counts = Template.objects.filter(user=self.request.user, is_delete=False).count()
        #     form_count += form_counts

        form_count = Template.objects.filter(user=self.request.user, is_delete=False).count()
        file_count = Files.objects.filter(user=self.request.user, is_delete=False).count()
        workflow_count = Workflow.objects.filter(user=self.request.user, is_delete=False).count()
        project_count = Project.objects.filter(user=self.request.user, is_delete=False).count()
        user= User.objects.filter(id=self.request.user.id)
        userdata=UsersSerializer(user,many=True)
        Userdata=userdata.data
        Data=json.loads(json.dumps(Userdata))
       
        return Response(
            {"form_count": form_count, "file_count": file_count, "workflow_count": workflow_count,
             "project_count": project_count, 'user':Data[0]},
            status=status.HTTP_200_OK)