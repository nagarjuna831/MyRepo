from users import views
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='user_register'),
    path('email-verify/', views.VerifyEmail.as_view(), name='email_verify'),
    path('profile/', views.UserUpdateViews.as_view(), name='user_profile'),
    path('update/<int:id>', views. UserProfileUpdateViews.as_view(), name='user_profile_update'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('all/', views.AllUserListView.as_view(), name='all_users'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',views.LogoutAPIView.as_view(), name="logout"),
    path('delete/<int:id>',views.DeleteAPIView.as_view(), name="delete"),
    path('request-reset-email/',views.RequestPasswordResetEmail.as_view(),name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',views.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete',views.SetNewPasswordAPIView.as_view(),name='password-reset-complete')
   
]