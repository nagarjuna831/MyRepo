from django.urls import path
from rest_framework.routers import DefaultRouter
from commons import views

router = DefaultRouter()
router.register(r'formdatapermissions', views.PermissionListViewSet, 'formdatapermissions')
router.register(r'templatepermissions', views.TemplatePermissionListViewSet, 'templatepermissions')
router.register(r'fieldpermissions', views.FieldPermissionListViewSet, 'fieldpermissions')
router.register(r'teams', views.TeamListViewSet, 'teams')
router.register(r'teampermissions', views.TeamPermissionListViewSet, 'teampermissions')
router.register(r'confurigations', views.ConfigurationSettingsViewSet, 'confurigation')
router.register(r'notification', views.NotificationViewSet, 'notification')

urlpatterns = [
    path('<int:id>/', views.PermissionListView.as_view()),
    path('formdatapermissions/<int:id>/', views.PermissionUpdateApi.as_view()),
    path('formdatapermissions/<int:id>/delete/', views.PermissionDeleteApi.as_view()),
    path('template/<int:id>/', views.PermissionTemplateListView.as_view()),
    path('<int:id>/', views.TemplatePermissionListView.as_view()),
    path('<int:id>/', views.FieldPermissionListView.as_view()),
    path('<int:id>/', views.TeamListView.as_view()),
    path('team/template/', views.TeamPermissionTemplateListView.as_view()),
    path('team/<int:template_id>/member/', views.TeamTemplateMemberView.as_view()),
    path('all/teams/', views.TeamTemplateView.as_view()),
    path('teams/user/', views.TeamListUserView.as_view()),
    path('team/<int:template_id>/reports/', views.TeamFormDataView.as_view()),
    path('defaultvalue/<int:template_id>/<int:field_id>/', views.UserPermissionsFieldsView.as_view()),
    path('team/lead/', views.TeamPermissionLeadListView.as_view()),
    path('team/<int:id>/user', views.TeamPermissionUserListView.as_view()),
    path('team/user/lead/', views.TeamListUserLeadView.as_view()),
    path('custom-form/', views.CustomFormView.as_view()),
    path('custom-form/<int:id>/', views.CustomFormListView.as_view()),
    
]
urlpatterns += router.urls