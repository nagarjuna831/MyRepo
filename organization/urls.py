from django.urls import path
from rest_framework.routers import DefaultRouter
from organization import views

router = DefaultRouter()

urlpatterns = [
    path('', views.OrganizationListCreateView.as_view(), name='organization'),
    path('<int:id>/', views.OrganizationRetrieveUpdateDeleteView.as_view(), name='organization_id'),
    path('member/', views.MemberCreateView.as_view(), name='member'),
    path('<int:id>/members/', views.OrganizationMemberListView.as_view(), name='organization_member'),
    path('<str:public_url>/check', views.OrganizationCheckView.as_view(), name='organization_check'),
]

urlpatterns += router.urls