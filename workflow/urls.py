from django.urls import path
from rest_framework.routers import DefaultRouter
from workflow import views

router = DefaultRouter()
router.register(r'state', views.StateViewSet, basename='state')
router.register(r'transition', views.TransitionViewSet, basename='transition')
router.register(r'template', views.TemplateWorkflowViewSet, basename='template_workflow')


urlpatterns = [
    path('', views.WorkflowListCreate.as_view(), name='workflow'),
    path('<int:id>/', views.WorkflowListView.as_view(), name='workflow_list'),
    path('<int:id>/state/', views.StateListView.as_view(), name='workflow_state'),
    path('state/<int:id>/transition/', views.StateTransitionListView.as_view(), name='state_transition'),
    path('action/', views.WorkflowActionView.as_view(), name='workflow_action'),
    path('data/<int:id>/action_log/', views.WorkflowInstanceLogView.as_view(), name='workflow_data_action_log'),
    path('instance/data/', views.WorkflowInstanceLogViews.as_view(), name='workflow_instance_data'),
    path('template/state/', views.WorkflowTemplateStateViews.as_view(), name='workflow_instance_state'),
    path('state/member/<int:template_id>/<int:user_id>/', views.WorkflowStateMemberViews.as_view()),
    path('<int:workflow_id>/transition', views.TransitionWorkflowView.as_view()),
]
urlpatterns += router.urls
