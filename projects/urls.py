from django.urls import path
from rest_framework.routers import DefaultRouter
from projects import views


router = DefaultRouter()
router.register(r'', views.ProjectListViewSet, 'projects')
urlpatterns = [
path('<int:id>/template/', views.ProjectTemplateListView.as_view()),
path('<int:id>/organization/', views.ProjectOrganizationListView.as_view()),
path('<int:id>/user/', views.ProjectUserListView.as_view())

]

urlpatterns += router.urls