from django.urls import path
from rest_framework.routers import DefaultRouter
from location import views

router = DefaultRouter()

urlpatterns = [
    path('', views.UserTrackingListCreateView.as_view(), name='location'),
    path('<int:id>/', views.LocationRetrieveUpdateDeleteView.as_view(), name='location_id'),
    path('user/<str:id>/<str:startdate>/<str:enddate>/', views.LocationRetrieView.as_view(), name='userlocation_id'),
   
]

urlpatterns += router.urls