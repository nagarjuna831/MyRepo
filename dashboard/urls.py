from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardStatsViews.as_view()),
]
