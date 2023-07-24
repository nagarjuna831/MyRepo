from django.urls import path
from rest_framework.routers import DefaultRouter
from systemlog import views

router = DefaultRouter()

urlpatterns = [
    path('', views.ActivityLogListView.as_view(), name='alllogs'),
    path('model/<str:model>/', views.ActivityLogModelListView.as_view(), name='modellogs'),
   
   
]

urlpatterns += router.urls