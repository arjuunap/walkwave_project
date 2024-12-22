from django.urls import path
from . import views

urlpatterns=[
    path('',views.admin_login,name='admin_login'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('admin_logout',views.admin_logout,name='admin_logout'),
    path('user_listing',views.user_listing,name='user_listing'),
    path('user_status/<int:user_id>/',views.user_status,name='user_status')

]