from django.urls import path
from rest_framework.routers import DefaultRouter
from subscription import views

router = DefaultRouter()
router.register(r'billings', views.BilingListViewSet, 'billings')


urlpatterns = [
    path('user/', views.BilingListUserViewSet.as_view()),
    path('alldata/', views.BilingSubscriptionView.as_view()),
    path('fetch-order/', views.FetchPaymentView.as_view()),  
    path('create-payment/', views.CreatePaymentView.as_view()) 
]
urlpatterns += router.urls