from django.urls import path
from rest_framework.routers import DefaultRouter
from forms import views 
router = DefaultRouter()
# router.register(r'fields', views.FieldListViewSet, 'fields')
router.register(r'data', views.FormDataListViewSet, 'form_data')
router.register(r'share', views.ShareFormViewSet, 'share_form')

urlpatterns = [
    path('', views.FormListView.as_view()),
    path('all/', views.FormListsView.as_view()),
    path('<int:id>/', views.FormUpdateList.as_view()),
    path('<int:id>/delete/', views.FormDeleteApiView.as_view()),
    path('fields/', views.FieldListViewSet.as_view()),
    path('fields/<int:id>/', views.FieldUpdateAPIView.as_view()),
    path('data/<int:id>/delete/', views.FormDataDeleteApiView.as_view()),
    path('<int:id>/users/', views.FormtUserListView.as_view()),
    path('template/<int:id>/fields/', views.FieldsListView.as_view()),
    path('template/field/', views.UpdateFields.as_view()),
    path('template/<int:id>/data/', views.FormDataListView.as_view()),
    path('template/<int:id>/users/', views.TemplateUserListView.as_view()),
    path('template/<int:id>/data/download/', views.FormDataListViewDownload.as_view()),
    path('template/<int:id>/share/', views.TemplateSharedListView.as_view()),
    path('data/<int:id>/action/', views.FormDataActionView.as_view()),
    path('feature/share/<str:token>/form/', views.SharedFormDataListView.as_view()),
    path('.', views.StoreSharedFormData.as_view()),
    path('feature/share/<str:token>/view/', views.ViewSharedFormData.as_view()),
    path('template/<int:id>/searchdata/', views.FormDataSearchListView.as_view()),
    path('template/<int:id>/<str:token>/searchdata/', views.FormDataSearchView.as_view()),
    path('formdata/comment/', views.FormDataCommentView.as_view()),
    path('formdata/comment/<int:id>/', views.FormDataCommentUpdateView.as_view()),
    path('formdata/<int:id>/comment/', views.FormDataCommentListView.as_view()),
    path('formdata/<int:template_id>/<int:field_id>/<str:value>/', views.FormDataValidateView.as_view()),
    path('template/<int:id>/reports/', views.FormDataView.as_view()),
    path('template/user/reports/', views.FormDataReportViews.as_view()),
    path('template/<int:id>/<str:token>/data/', views.FormDataListToeknView.as_view()),
    path('feature/share/<str:token>/store/', views.StoreSharedFormData.as_view()),
    path('field/style/', views.TemplateFieldStyleView.as_view()),
    path('field/style/<int:id>/', views.TemplateFieldStyleUpdateAPIView.as_view()),
    path('template/<int:id>/advancedsearch/', views.FormDataAdvancedSearchView.as_view()),
    
   
]
urlpatterns += router.urls
